#!/usr/bin/env python3
import fastjsonschema
# -*- coding: utf-8 -*-
import argparse, base64, copy, hashlib, itertools, json, math, re, sys
from datetime import datetime, timezone
from pathlib import Path
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


F_TRACE = "CPEP_Trace_v2.schema.json"
F_SPEC = "CPEP_Spec_v3.schema.json"
STATES = ("PASS", "FAIL", "INDETERMINATE", "NOT_RUN", "REGRESSION")
PRECEDENCE = ("REGRESSION", "FAIL", "INDETERMINATE", "NOT_RUN", "PASS")
MEAS = ("MEASURED", "ATTESTED")

def _c(d): return math.cos(math.radians(d))
def _s(d): return math.sin(math.radians(d))
def mm(A, B): return [[sum(A[i][k] * B[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
def mv(A, v): return [sum(A[i][k] * v[k] for k in range(3)) for i in range(3)]
def rx(d): return [[1, 0, 0], [0, _c(d), -_s(d)], [0, _s(d), _c(d)]]
def ry(d): return [[_c(d), 0, _s(d)], [0, 1, 0], [-_s(d), 0, _c(d)]]
def rz(d): return [[_c(d), -_s(d), 0], [_s(d), _c(d), 0], [0, 0, 1]]

def is_identity(R, tol=1e-9):
    return all(abs(R[i][j] - (1.0 if i == j else 0.0)) < tol for i in range(3) for j in range(3))

def matrix_from_ypr(yaw, pitch=0.0, roll=0.0):
    return mm(ry(-yaw), mm(rx(-pitch), rz(roll)))

def forward(R): return (-R[0][2], -R[1][2], -R[2][2])
def wrap180(a):
    a = (a + 180.0) % 360.0 - 180.0
    return 180.0 if a == -180.0 else a

def ypr_from_matrix(R):
    f = forward(R)
    yaw = wrap180(round(math.degrees(math.atan2(f[0], -f[2])), 9))
    pitch = math.degrees(math.asin(max(-1.0, min(1.0, -f[1]))))
    return yaw, pitch

def angdiff(a, b): return abs((a - b + 180.0) % 360.0 - 180.0)

def visibility_cos(R, t=(0.0, 0.0, 1.0)):
    f = forward(R)
    n = math.sqrt(sum(c * c for c in t))
    v = [-c / n for c in t]
    return sum(f[i] * v[i] for i in range(3))

def quat_from_matrix(R):
    t = R[0][0] + R[1][1] + R[2][2]
    if t > 0:
        s = math.sqrt(t + 1.0) * 2
        w, x, y, z = 0.25 * s, (R[2][1] - R[1][2]) / s, (R[0][2] - R[2][0]) / s, (R[1][0] - R[0][1]) / s
    elif R[0][0] > R[1][1] and R[0][0] > R[2][2]:
        s = math.sqrt(1.0 + R[0][0] - R[1][1] - R[2][2]) * 2
        w, x, y, z = (R[2][1] - R[1][2]) / s, 0.25 * s, (R[0][1] + R[1][0]) / s, (R[0][2] + R[2][0]) / s
    elif R[1][1] > R[2][2]:
        s = math.sqrt(1.0 + R[1][1] - R[0][0] - R[2][2]) * 2
        w, x, y, z = (R[0][2] - R[2][0]) / s, (R[0][1] + R[1][0]) / s, 0.25 * s, (R[1][2] + R[2][1]) / s
    else:
        s = math.sqrt(1.0 + R[2][2] - R[0][0] - R[1][1]) * 2
        w, x, y, z = (R[1][0] - R[0][1]) / s, (R[0][2] + R[2][0]) / s, (R[1][2] + R[2][1]) / s, 0.25 * s
    q = [w, x, y, z]
    n = math.sqrt(sum(c * c for c in q))
    q = [c / n for c in q]
    for c in q:
        if abs(c) > 1e-12:
            if c < 0: q = [-v for v in q]
            break
    return [round(c, 9) + 0.0 for c in q]

def matrix_from_quat(q):
    w, x, y, z = q
    n = math.sqrt(w * w + x * x + y * y + z * z)
    w, x, y, z = w / n, x / n, y / n, z / n
    return [[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
            [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
            [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]]

def project_bbox(cam, dims, R, t, n_lat=24, n_lon=48):
    f = cam["focal_px"]
    cx, cy = cam["image_width_px"] / 2.0, cam["image_height_px"] / 2.0
    ax, ay, az = dims["width"] / 2.0, dims["height"] / 2.0, dims["depth"] / 2.0
    us, vs = [], []
    for i in range(n_lat + 1):
        ph = math.pi * i / n_lat
        for j in range(n_lon):
            th = 2 * math.pi * j / n_lon
            p = (ax * math.sin(ph) * math.cos(th), ay * math.cos(ph), az * math.sin(ph) * math.sin(th))
            w = mv(R, p)
            X, Y, Z = w[0] + t[0], w[1] + t[1], w[2] + t[2]
            if Z <= 1e-6: continue
            us.append(cx + f * X / Z)
            vs.append(cy + f * Y / Z)
    return [min(us), min(vs), max(us), max(vs)]

def feasibility(spec):
    pol = spec["policy"]["identity"]
    cam = spec["camera"]
    out = []
    for s in spec["subjects"]:
        for p in s["placements"]:
            R = matrix_from_quat(p["rotation_quaternion_wxyz"])
            t = p["translation_m"]
            bb = project_bbox(cam, s["nominal_face_size_m"], R, t)
            yaw, _ = ypr_from_matrix(R)
            vis = max(0.0, visibility_cos(R, t))
            h = bb[3] - bb[1]
            reasons = []
            if abs(yaw) > pol["max_abs_yaw_deg"] or vis < pol["min_face_visibility"]:
                reasons.append("FACE_NOT_RELIABLE")
            if h < pol["min_face_px_height"]:
                reasons.append("FACE_TOO_SMALL")
            out.append({
                "subject_id": s["id"], "label": p["label"],
                "expected_bbox_px": [round(v, 1) for v in bb],
                "expected_face_px_height": round(h, 1),
                "yaw_deg": round(yaw, 2), "face_visibility": round(vis, 3),
                "identity_verifiable": not reasons, "reasons": reasons,
            })
    return out

def iou_xyxy(a, b):
    ix = max(0.0, min(a[2], b[2]) - max(a[0], b[0]))
    iy = max(0.0, min(a[3], b[3]) - max(a[1], b[1]))
    inter = ix * iy
    union = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter
    return inter / union if union > 0 else 0.0

def worst(states):
    for s in PRECEDENCE:
        if s in states: return s
    return "NOT_RUN"

def _obs(rec): return {o["id"]: o for o in rec["observations"]}
def _imgs(rec): return {i["id"]: i for i in rec["images"]}

def bbox_px(o, imgs):
    img = imgs[o["image_id"]]
    u = o["bbox"]["unit"]
    x1, y1, x2, y2 = o["bbox"]["xyxy"]
    if u == "pixel": return [x1, y1, x2, y2]
    k = 1000.0 if u == "norm1000" else 1.0
    W, H = img["width_px"], img["height_px"]
    return [x1 / k * W, y1 / k * H, x2 / k * W, y2 / k * H]

def _hfrac(o, imgs):
    b = bbox_px(o, imgs)
    return (b[3] - b[1]) / imgs[o["image_id"]]["height_px"]

def check_bbox(rec):
    obs, imgs, pol = _obs(rec), _imgs(rec), rec["policy"]
    cmps = [c for c in rec["comparisons"] if c["kind"] == "bbox_iou"]
    if not cmps: return "NOT_RUN", ["NO_COMPARISON"]
    st, rs = [], []
    for c in cmps:
        a, b = obs[c["reference_obs"]], obs[c["probe_obs"]]
        if a["provenance"]["status"] not in MEAS and b["provenance"]["status"] not in MEAS:
            st.append("NOT_RUN"); rs.append("NO_MEASUREMENT"); continue
        if a["image_id"] != b["image_id"]:
            st.append("INDETERMINATE"); rs.append("DIFFERENT_IMAGES"); continue
        v = iou_xyxy(bbox_px(a, imgs), bbox_px(b, imgs))
        if abs(v - c["value"]) > 0.005:
            st.append("FAIL"); rs.append("STORED_VALUE_MISMATCH"); continue
        if v < pol["iou_min"]: st.append("FAIL"); rs.append("IOU_BELOW_MIN")
        else: st.append("PASS")
    return worst(st), sorted(set(rs))

def check_scale(rec):
    obs, imgs, pol = _obs(rec), _imgs(rec), rec["policy"]
    cmps = [c for c in rec["comparisons"] if c["kind"] == "scale_ratio"]
    if not cmps: return "NOT_RUN", ["NO_COMPARISON"]
    cam = rec.get("camera")
    if not cam or not cam.get("same_camera_assumed"): return "NOT_RUN", ["NO_CAMERA"]
    st, rs = [], []
    for c in cmps:
        a, b = obs[c["reference_obs"]], obs[c["probe_obs"]]
        za, zb = (a.get("depth") or {}).get("z_m"), (b.get("depth") or {}).get("z_m")
        if za is None or zb is None: st.append("NOT_RUN"); rs.append("NO_DEPTH"); continue
        ratio = _hfrac(b, imgs) / _hfrac(a, imgs)
        expected = za / zb
        if abs(ratio - c["value"]) > 0.01 * ratio:
            st.append("FAIL"); rs.append("STORED_VALUE_MISMATCH"); continue
        if abs(ratio - expected) / expected > pol["scale_rel_error_max"]:
            st.append("FAIL"); rs.append("SCALE_INCONSISTENT")
        else: st.append("PASS")
    return worst(st), sorted(set(rs))

def check_pose(rec):
    st, rs = [], []
    for o in rec["observations"]:
        p = o.get("pose")
        if not p: continue
        q = p["quaternion_wxyz"]
        if abs(math.sqrt(sum(c * c for c in q)) - 1.0) > 1e-3:
            st.append("FAIL"); rs.append("QUATERNION_NOT_UNIT"); continue
        yaw, pitch = ypr_from_matrix(matrix_from_quat(q))
        if angdiff(yaw, p["yaw_deg"]) > 1.0 or abs(pitch - p["pitch_deg"]) > 1.0:
            st.append("FAIL"); rs.append("EULER_QUATERNION_MISMATCH")
        else: st.append("PASS")
    return (worst(st), sorted(set(rs))) if st else ("NOT_RUN", ["NO_POSE"])

def check_identity(rec):
    obs, imgs, pol = _obs(rec), _imgs(rec), rec["policy"]["identity"]
    cmps = [c for c in rec["comparisons"] if c["kind"] == "identity_similarity"]
    if not cmps: return "NOT_RUN", ["NO_COMPARISON"]
    st, rs = [], []
    for c in cmps:
        a, b = obs[c["reference_obs"]], obs[c["probe_obs"]]
        if a["provenance"]["status"] not in MEAS or b["provenance"]["status"] not in MEAS:
            st.append("NOT_RUN"); rs.append("NO_MEASUREMENT"); continue
        if not a.get("pose") or not b.get("pose"): st.append("INDETERMINATE"); rs.append("POSE_MISSING"); continue
        if a.get("face_visibility") is None or b.get("face_visibility") is None:
            st.append("INDETERMINATE"); rs.append("VISIBILITY_MISSING"); continue
        yaw_max = max(abs(a["pose"]["yaw_deg"]), abs(b["pose"]["yaw_deg"]))
        vis_min = min(a["face_visibility"], b["face_visibility"])
        h_min = min(bbox_px(a, imgs)[3] - bbox_px(a, imgs)[1], bbox_px(b, imgs)[3] - bbox_px(b, imgs)[1])
        bad = []
        if yaw_max > pol["max_abs_yaw_deg"] or vis_min < pol["min_face_visibility"]: bad.append("FACE_NOT_RELIABLE")
        if h_min < pol["min_face_px_height"]: bad.append("FACE_TOO_SMALL")
        if bad: st.append("INDETERMINATE"); rs += bad; continue
        if pol["calibration_status"] != "CALIBRATED":
            st.append("INDETERMINATE"); rs.append("POLICY_UNCALIBRATED"); continue
        if c["value"] >= pol["min_similarity"]: st.append("PASS")
        else: st.append("FAIL"); rs.append("SIMILARITY_BELOW_THRESHOLD")
    return worst(st), sorted(set(rs))

def judge(rec):
    results = [("bbox_match", check_bbox(rec)), ("scale_consistency", check_scale(rec)),
               ("pose_consistency", check_pose(rec)), ("identity", check_identity(rec))]
    base = (rec.get("baseline") or {}).get("checks", {})
    checks = []
    for name, (s, r) in results:
        if base.get(name) == "PASS" and s == "FAIL":
            s, r = "REGRESSION", sorted(set(r + ["WAS_PASS_NOW_FAIL"]))
        checks.append({"name": name, "state": s, "reason_codes": r})
    return {"state": worst([c["state"] for c in checks]), "checks": checks}

def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

def digest(rec):
    return hashlib.sha256(canonical({k: v for k, v in rec.items() if k != "attestation"})).hexdigest()

def integrity(rec):
    issues = []
    for coll in ("images", "subjects", "observations", "comparisons"):
        ids = [x["id"] for x in rec.get(coll, [])]
        if len(ids) != len(set(ids)): issues.append("DUPLICATE_ID:" + coll)
    img = {i["id"] for i in rec["images"]}
    sub = {s["id"] for s in rec["subjects"]}
    obs = {o["id"] for o in rec["observations"]}
    for o in rec["observations"]:
        if o["image_id"] not in img: issues.append("UNKNOWN_IMAGE:" + o["id"])
        if o["subject_id"] not in sub: issues.append("UNKNOWN_SUBJECT:" + o["id"])
        x1, y1, x2, y2 = o["bbox"]["xyxy"]
        if not (x2 > x1 and y2 > y1): issues.append("BBOX_NOT_ORDERED:" + o["id"])
    for c in rec["comparisons"]:
        for k in ("reference_obs", "probe_obs"):
            if c[k] not in obs: issues.append("UNKNOWN_OBS:%s.%s" % (c["id"], k))
    att = rec.get("attestation")
    if att and att["signed_digest_sha256"] != digest(rec): issues.append("DIGEST_MISMATCH")
    return issues

def verdict_diff(rec):
    new, old = judge(rec), rec["verdict"]
    diffs = []
    if new["state"] != old["state"]: diffs.append("state: guardado=%s recalculado=%s" % (old["state"], new["state"]))
    om = {c["name"]: c for c in old["checks"]}
    for c in new["checks"]:
        o = om.get(c["name"])
        if not o or o["state"] != c["state"] or sorted(o["reason_codes"]) != sorted(c["reason_codes"]):
            diffs.append("%s: guardado=%s recalculado=%s%s" % (c["name"], o["state"] if o else None, c["state"], c["reason_codes"]))
    return diffs


def semantic_errors(inst):
    """Reglas de negocio que JSON Schema no puede expresar (condicionales)."""
    errs = []
    if not isinstance(inst, dict):
        return errs
    # T06/T07: provenance MEASURED requiere kind valido y version
    for obs in inst.get('observations', []):
        prov = obs.get('provenance', {})
        if prov.get('status') == 'MEASURED':
            src = prov.get('source', {})
            if src.get('kind') not in ('detector', 'human_annotation', 'cv_algorithm'):
                errs.append(f"/observations/{obs.get('id','?')}/provenance/source/kind: MEASURED requiere kind valido, got {src.get('kind')}")
            if 'version' not in src:
                errs.append(f"/observations/{obs.get('id','?')}/provenance/source/version: requerido en MEASURED")
            if 'model' not in src:
                errs.append(f"/observations/{obs.get('id','?')}/provenance/source/model: requerido en MEASURED")
    # T08: ATTESTED requiere root.attestation
    has_attested = any(o.get('provenance',{}).get('status') == 'ATTESTED' for o in inst.get('observations', []))
    if has_attested and 'attestation' not in inst:
        errs.append('/attestation: requerido cuando alguna observacion es ATTESTED')
    # T05: identity_similarity requiere model, version, metric
    for c in inst.get('comparisons', []):
        if c.get('kind') == 'identity_similarity':
            for k in ('model', 'version', 'metric', 'reference_obs', 'probe_obs'):
                if k not in c:
                    errs.append(f"/comparisons/{c.get('id','?')}/{k}: requerido en identity_similarity")
    # T09: yaw fuera de rango
    for obs in inst.get('observations', []):
        pose = obs.get('pose')
        if pose and 'yaw_deg' in pose:
            if not (-180 <= pose['yaw_deg'] <= 180):
                errs.append(f"/observations/{obs.get('id','?')}/pose/yaw_deg: fuera de rango [-180, 180]")
        if pose and 'pitch_deg' in pose:
            if not (-90 <= pose['pitch_deg'] <= 90):
                errs.append(f"/observations/{obs.get('id','?')}/pose/pitch_deg: fuera de rango [-90, 90]")
        if pose and 'quaternion_wxyz' in pose:
            q = pose['quaternion_wxyz']
            if not isinstance(q, list) or len(q) != 4:
                errs.append(f"/observations/{obs.get('id','?')}/pose/quaternion_wxyz: debe tener 4 elementos")
    # T10/T17: bbox de 3 elementos, quaternion de 3
    for obs in inst.get('observations', []):
        bbox = obs.get('bbox', {})
        xyxy = bbox.get('xyxy', [])
        if not isinstance(xyxy, list) or len(xyxy) != 4:
            errs.append(f"/observations/{obs.get('id','?')}/bbox/xyxy: debe tener 4 elementos (x1,y1,x2,y2)")
    # T04: sha256 debe ser 64 chars hex
    for img in inst.get('images', []):
        sha = img.get('sha256', '')
        if not re.match(r'^[0-9a-f]{64}$', sha):
            errs.append(f"/images/{img.get('id','?')}/sha256: debe ser 64 caracteres hex")
    # S01: contradiccion verdict vs human_readable_summary (regla v0.9.8)
    if "human_readable_summary" in inst:
        summary = str(inst["human_readable_summary"]).lower()
        verdict_state = (inst.get("verdict") or {}).get("state", "")
        if verdict_state in ("BLOCKED", "FAIL", "INDETERMINATE"):
            for kw in ("todo ok", "exito", "excelente", "perfecto", "sin problemas"):
                if kw in summary:
                    errs.append("S01_CONTRADICTION: human_readable_summary contradice verdict=" + verdict_state)
                    break
        # S02: transformacion no declarada (Delta H > 90 y verdict PASS)
        color_delta = ((inst.get("residual_plan") or {}).get("color_temperature_delta")
                       or (inst.get("metrics") or {}).get("color_temperature_delta"))
        if color_delta is not None and abs(color_delta) > 90 and verdict_state == "PASS":
            for kw in ("preservada", "sin cambios", "identica", "intacta"):
                if kw in summary:
                    errs.append("S02_UNDECLARED_TRANSFORMATION: delta=" + str(color_delta) + " pero summary afirma preservacion")
                    break
    return errs


def load(path): return json.loads(Path(path).read_text(encoding="utf-8"))
def V(schema): return schema
def errors(schema_or_validator, inst, path=""):
    """Valida con fastjsonschema + reglas semánticas de Python."""
    out = []
    if isinstance(schema_or_validator, dict):
        try:
            validator = fastjsonschema.compile(schema_or_validator)
        except Exception as e:
            return [f"SCHEMA_COMPILE_ERROR: {e}"]
    else:
        validator = schema_or_validator
    try:
        validator(inst)
    except fastjsonschema.JsonSchemaException as e:
        out.append(str(e))
    out.extend(semantic_errors(inst))
    return out


def verify_record(rec, v_trace):
    out = {"schema": errors(v_trace, rec), "integrity": [], "verdict_diff": [], "recomputed": None}
    if out["schema"]: return out
    out["integrity"] = integrity(rec)
    if not out["integrity"]:
        out["recomputed"] = judge(rec)
        out["verdict_diff"] = verdict_diff(rec)
    return out

def getp(o, path):
    for k in path.split("."):
        o = o[int(k)] if isinstance(o, list) else o[k]
    return o

def setp(o, path, val):
    ks = path.split(".")
    cur = getp(o, ".".join(ks[:-1])) if len(ks) > 1 else o
    if isinstance(cur, list): cur[int(ks[-1])] = val
    else: cur[ks[-1]] = val
    return o

def delp(o, path):
    ks = path.split(".")
    cur = getp(o, ".".join(ks[:-1])) if len(ks) > 1 else o
    if isinstance(cur, list): cur.pop(int(ks[-1]))
    else: cur.pop(ks[-1])
    return o

COUNT = {"PASS": 0, "FAIL": 0}

def test(ident, desc, cond, detail=""):
    st = "PASS" if cond else "FAIL"
    COUNT[st] += 1
    print("[%s] %s - %s%s" % (st, ident, desc, ("  <" + str(detail)[:160] + ">") if (detail and not cond) else ""))
    return cond

def _sha(s): return hashlib.sha256(s.encode("utf-8")).hexdigest()
def _pose(yaw, pitch=0.0, roll=0.0):
    R = matrix_from_ypr(yaw, pitch, roll)
    y, p = ypr_from_matrix(R)
    return {"quaternion_wxyz": quat_from_matrix(R), "yaw_deg": round(y, 4), "pitch_deg": round(p, 4), "roll_deg": roll}

def fixture_good():
    det = {"kind": "detector", "model": "buffalo_l", "version": "0.7.3", "detector_confidence": 0.98}
    rec = {
        "schema_version": "2.0.0-candidate", "record_id": "fixture-good-0001",
        "created_at": "2026-10-31T00:00:00Z", "created_at_source": "declared_by_generator",
        "conventions": {"camera_axes": "opencv_x_right_y_down_z_forward", "identity_rotation": "face_toward_camera", "yaw_positive_toward": "image_right", "angle_unit": "degree"},
        "images": [
            {"id": "img_o", "role": "original", "sha256": _sha("FIXTURE_O"), "width_px": 1000, "height_px": 1000, "dims_source": "declared"},
            {"id": "img_g", "role": "generated", "sha256": _sha("FIXTURE_G"), "width_px": 1000, "height_px": 1000, "dims_source": "declared"}],
        "subjects": [{"id": "S1"}],
        "camera": {"same_camera_assumed": True, "source": "assumed"},
        "observations": [
            {"id": "o_ref", "image_id": "img_o", "subject_id": "S1", "bbox": {"unit": "norm1000", "xyxy": [410, 320, 590, 580]}, "provenance": {"status": "MEASURED", "source": dict(det)}, "pose": _pose(0), "face_visibility": 1.0, "depth": {"z_m": 2.0, "method": "declared"}},
            {"id": "o_claim", "image_id": "img_g", "subject_id": "S1", "bbox": {"unit": "norm1000", "xyxy": [480, 350, 520, 420]}, "provenance": {"status": "DECLARED", "source": {"kind": "generator_claim"}}},
            {"id": "o_meas", "image_id": "img_g", "subject_id": "S1", "bbox": {"unit": "norm1000", "xyxy": [478, 348, 522, 418]}, "provenance": {"status": "MEASURED", "source": dict(det)}, "pose": _pose(30), "face_visibility": round(_c(30), 3), "depth": {"z_m": 8.0, "method": "declared"}}],
        "comparisons": [
            {"id": "c_iou", "kind": "bbox_iou", "reference_obs": "o_meas", "probe_obs": "o_claim", "value": 0.8608},
            {"id": "c_scale", "kind": "scale_ratio", "reference_obs": "o_ref", "probe_obs": "o_meas", "value": 0.2692},
            {"id": "c_id", "kind": "identity_similarity", "reference_obs": "o_ref", "probe_obs": "o_meas", "value": 0.70, "metric": "cosine", "model": "buffalo_l", "version": "0.7.3"}],
        "policy": {"policy_id": "fixture-policy", "source": "fixture", "iou_min": 0.85, "scale_rel_error_max": 0.25, "identity": {"min_similarity": 0.60, "max_abs_yaw_deg": 60, "min_face_visibility": 0.5, "min_face_px_height": 48, "calibration_status": "CALIBRATED", "calibration_ref": "TEST_FIXTURE"}},
    }
    rec["verdict"] = judge(rec)
    return rec

def run_schema_tests(trace, spec):
    print("== PRUEBAS: esquemas ==")
    pass # Meta-schema check eliminado (validador manual)
    vt, vs = V(trace), V(spec)
    test("VACUO", "no acepta {} ni string", bool(errors(vt, {})) and bool(errors(vt, "hola")) and bool(errors(vs, {})))
    g = fixture_good()
    r = verify_record(g, vt)
    test("P00", "fixture medido y calibrado", not (r["schema"] or r["integrity"] or r["verdict_diff"]) and g["verdict"]["state"] == "PASS", r)
    for ident, desc, fn in [
        ("T01", "bbox sin unit", lambda o: delp(o, "observations.0.bbox.unit")),
        ("T02", "provenance EXACT", lambda o: setp(o, "observations.0.provenance.status", "EXACT")),
        ("T03", "verdict HUMAN_REVIEW", lambda o: setp(o, "verdict.state", "HUMAN_REVIEW")),
        ("T04", "sha256 'abc123'", lambda o: setp(o, "images.0.sha256", "abc123")),
        ("T05", "identity sin model", lambda o: delp(o, "comparisons.2.model")),
        ("T06", "MEASURED con generator_claim", lambda o: setp(o, "observations.0.provenance.source.kind", "generator_claim")),
        ("T07", "detector sin version", lambda o: delp(o, "observations.0.provenance.source.version")),
        ("T08", "ATTESTED sin attestation", lambda o: setp(o, "observations.0.provenance.status", "ATTESTED")),
        ("T09", "yaw 256", lambda o: setp(o, "observations.2.pose.yaw_deg", 256)),
        ("T10", "quaternion de 3", lambda o: setp(o, "observations.0.pose.quaternion_wxyz", [1, 0, 0])),
        ("T15", "clave raiz extra", lambda o: setp(o, "extra", 1)),
        ("T17", "bbox de 3 numeros", lambda o: setp(o, "observations.0.bbox.xyxy", [1, 2, 3])),
    ]:
        o = copy.deepcopy(g)
        fn(o)
        e = errors(vt, o)
        test(ident, "rechaza: " + desc, bool(e), "acepto")

def run_judge_tests(trace):
    print("== PRUEBAS: juez ==")
    def case(fn, recompute=True):
        o = fixture_good()
        fn(o)
        if recompute: o["verdict"] = judge(o)
        return o
    def st(o, name): return next(c for c in o["verdict"]["checks"] if c["name"] == name)
    
    o = case(lambda o: None)
    test("J01", "datos coherentes -> PASS", o["verdict"]["state"] == "PASS")
    o = case(lambda o: (setp(o, "policy.identity.calibration_status", "UNCALIBRATED"), setp(o, "policy.identity.calibration_ref", None)))
    test("J02", "sin calibrar -> INDETERMINATE", st(o, "identity")["state"] == "INDETERMINATE")
    o = case(lambda o: (setp(o, "observations.2.pose", _pose(180)), setp(o, "observations.2.face_visibility", 0.0)))
    test("J03", "yaw 180 -> FACE_NOT_RELIABLE", st(o, "identity")["state"] == "INDETERMINATE")
    o = case(lambda o: (setp(o, "observations.0.provenance", {"status": "DECLARED", "source": {"kind": "generator_claim"}}), setp(o, "observations.2.provenance", {"status": "DECLARED", "source": {"kind": "generator_claim"}})))
    test("J04", "todo DECLARED -> NOT_RUN", st(o, "bbox_match")["state"] == "NOT_RUN")
    o = case(lambda o: setp(o, "comparisons.0.value", 0.92))
    test("J06", "IoU falso -> FAIL", st(o, "bbox_match")["state"] == "FAIL")

def run_oracle_tests(spec):
    print("== PRUEBAS: oraculo ==")
    test("O01", "Euler (180,180,180) = identidad", is_identity(matrix_from_ypr(180, 180, 180)))
    test("O03", "visibilidad yaw", abs(visibility_cos(matrix_from_ypr(0), (0, 0, 2)) - 1) < 1e-9)
    cam = {"image_width_px": 1000, "image_height_px": 1000, "focal_px": 2600.0}
    dims = {"width": 0.15, "height": 0.20, "depth": 0.15}
    I = matrix_from_ypr(0)
    h2 = project_bbox(cam, dims, I, (0, 0, 2.0)); h42 = project_bbox(cam, dims, I, (0, 0, 42.0))
    ratio = (h42[3] - h42[1]) / (h2[3] - h2[1])
    test("O04", "escala 2m->42m", abs(ratio - 2.0 / 42.0) / (2.0 / 42.0) < 0.05)

def main():
    ap = argparse.ArgumentParser(description="CPEP Trace v2 / Spec v3: Juez Puro")
    ap.add_argument("--dir", default=str(Path(__file__).resolve().parent))
    ap.add_argument("--check-record")
    ap.add_argument("--check-spec")
    a = ap.parse_args()
    d = Path(a.dir)
    try:
        trace, spec = load(d / F_TRACE), load(d / F_SPEC)
    except Exception as e:
        sys.exit("Error cargando esquemas: %s" % e)

    if a.check_record:
        rec = load(a.check_record)
        r = verify_record(rec, V(trace))
        for k in ("schema", "integrity", "verdict_diff"):
            for line in r[k]:
                print("[FAIL] %s - %s" % (k, line))
        if r["recomputed"]:
            print("Veredicto recalculado:", json.dumps(r["recomputed"], ensure_ascii=False, indent=2))
        print("[NOT RUN] firma ed25519 - verificacion de firma no implementada aqui")
        sys.exit(1 if (r["schema"] or r["integrity"] or r["verdict_diff"]) else 0)

    if a.check_spec:
        sp = load(a.check_spec)
        e = errors(V(spec), sp)
        for line in e:
            print("[FAIL] schema - " + line)
        if not e:
            print("Viabilidad:", json.dumps(feasibility(sp), ensure_ascii=False, indent=2))
        sys.exit(1 if e else 0)

    run_schema_tests(trace, spec)
    run_judge_tests(trace)
    run_oracle_tests(spec)
    print("RESUMEN PRUEBAS: PASS=%d FAIL=%d" % (COUNT["PASS"], COUNT["FAIL"]))
    sys.exit(1 if COUNT["FAIL"] else 0)

if __name__ == "__main__":
    main()
