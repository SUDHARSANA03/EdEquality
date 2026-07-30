import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

target_files = [
    os.path.join(os.path.dirname(__file__), "frontend", "index.html"),
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "index.html")
]

for filepath in target_files:
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        continue
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Update normalizeSubjectName
    target_str1 = """    function normalizeSubjectName(subj) {
      const s = (subj || "").toString().toLowerCase().trim();
      if (s.includes("math") || s.includes("algebra") || s.includes("calc")) return "Mathematics";
      if (s.includes("bio") || s.includes("botan") || s.includes("zoo")) return "Biology";
      if (s.includes("chem")) return "Chemistry";
      if (s.includes("social") || s.includes("hist") || s.includes("civ") || s.includes("geog")) return "Social Studies";
      if (s.includes("env") || s.includes("evs")) return "Environmental Science";
      if (s.includes("phys")) return "Physics";
      return "English Grammar";
    }"""

    replacement_str1 = """    function normalizeSubjectName(subj) {
      const s = (subj || "").toString().toLowerCase().trim();
      if (s.includes("math") || s.includes("algebra") || s.includes("calc") || s.includes("arithmetic") || s.includes("geom") || s.includes("trig") || s.includes("stat") || s.includes("fraction") || s.includes("num") || s.includes("equation") || s.includes("poly")) return "Mathematics";
      if (s.includes("bio") || s.includes("botan") || s.includes("zoo")) return "Biology";
      if (s.includes("chem")) return "Chemistry";
      if (s.includes("social") || s.includes("hist") || s.includes("civ") || s.includes("geog")) return "Social Studies";
      if (s.includes("env") || s.includes("evs")) return "Environmental Science";
      if (s.includes("phys")) return "Physics";
      if (s.includes("eng") || s.includes("gram")) return "English Grammar";
      return "Mathematics";
    }"""

    if target_str1 in content:
        content = content.replace(target_str1, replacement_str1)
        print(f"Updated normalizeSubjectName in {filepath}")
    else:
        print(f"target_str1 not found in {filepath}")

    # 2. Update renderSubjectCurriculum backend override condition
    target_str2 = """    function renderSubjectCurriculum(selectedSubj, data = null) {
      let currentSubj = selectedSubj;
      if (data && data.detected_subject) {
        if (!selectedSubj || selectedSubj === "auto" || normalizeSubjectName(selectedSubj) === normalizeSubjectName(data.detected_subject)) {
          currentSubj = data.detected_subject;
        }
      }"""

    replacement_str2 = """    function renderSubjectCurriculum(selectedSubj, data = null) {
      let currentSubj = selectedSubj;
      if (data && data.detected_subject && data.detected_subject.toLowerCase() !== "auto") {
        currentSubj = data.detected_subject;
      }"""

    if target_str2 in content:
        content = content.replace(target_str2, replacement_str2)
        print(f"Updated renderSubjectCurriculum in {filepath}")
    else:
        print(f"target_str2 not found in {filepath}")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

print("HTML updates complete!")
