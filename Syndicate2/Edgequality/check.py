import re
content = open(r'c:\Syndicate2\Edgequality\frontend\index.html', encoding='utf-8').read()
views = re.findall(r'id="view-[^"]+"', content)
print("Found views:", views)
