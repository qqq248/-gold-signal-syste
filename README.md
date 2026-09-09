# Gold Signal System

نظام تحليلي فقط لإنتاج توصية يومية واحدة لـ XAUUSD أو `NO TRADE`. لا يحتوي أي تكامل لتنفيذ الصفقات ولا يطلب بيانات دخول وسيط.

## التشغيل

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
cp .env.example .env
python main.py
```

المصدر الافتراضي هو Twelve Data للزوج الفوري `XAU/USD`. أنشئ API key وضعه في `.env` تحت `TWELVE_DATA_API_KEY`. كل ضغطة على `ANALYZE GOLD NOW` تجلب شموعًا حديثة، تعيد التحليل، وتحفظ نتيجة مستقلة. لا يوجد قفل يومي. يمكن استخدام CSV حقيقي عبر `PRICE_PROVIDER=csv`. لن يختلق النظام بيانات عند تعذر المصدر.

الواجهة: `streamlit run dashboard/app.py`. المجدول: `python scheduler.py`. الاختبارات: `pytest -q`.

## ضوابط مهمة

- لا يوجد قفل يومي: كل طلب يدوي ينتج تحليلًا جديدًا وقد يظل القرار `NO TRADE` إذا لم تتحقق الشروط.
- كل تحليل من الواجهة يُحفظ في السجل للمراجعة.
- التحليل الأساسي محايد إلى أن يزوّد Adapter اقتصادي موثوق بالسياق. غياب الأخبار يرفع المخاطر ولا يعني عدم وجود أخبار.
- نتائج Backtest لا تُعرض كنسبة نجاح حقيقية إلا بعد تمرير بيانات تاريخية حقيقية ملائمة ودون تسرب زمني.
- هذا النظام أداة بحث، وليس ضمانًا أو نصيحة مالية.
