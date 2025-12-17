# mustafatik

مكتبة بايثون مساعدة لتوليد بيانات الأجهزة ووكلاء المستخدم (User-Agents) بشكل عشوائي ومحاكي للأجهزة الحقيقية.

## التثبيت

```bash
pip install mustafatik
```

## الاستخدام

```python
from mustafatik import mustafatik

# إنشاء كائن من المكتبة
device_generator = mustafatik()

# توليد بيانات جهاز عشوائية
device_data = device_generator._device()
print(device_data)

# تحديث المعاملات (params) ورؤوس الطلب (headers)
params = {"key1": "value1"}
headers = {"Accept": "*/*"}

updated_params = device_generator.updateParams(params)
updated_headers = device_generator.updateHeaders(headers)

print(updated_params)
print(updated_headers)
```

## المطور

مصطفى
تليجرام: @PPH9P
