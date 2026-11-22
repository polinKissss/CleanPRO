const form = document.getElementById('callback-form');

if (form) {
    const emailRe = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
    const phoneRe = /^\+?[\d\s()-]{10,20}$/;

    const rules = {
        name:     v => v.trim().length >= 2   || 'Укажите имя (минимум 2 символа)',
        phone:    v => phoneRe.test(v.trim()) || 'Проверьте формат телефона',
        email:    v => !v.trim() || emailRe.test(v.trim()) || 'Проверьте формат почты',
        message:  v => v.trim().length >= 10  || 'Опишите задачу подробнее (минимум 10 символов)',
    };

    function validateField(input) {
        const box = form.querySelector(`[data-error-for="${input.name}"]`);
        const rule = rules[input.name];
        if (!box || !rule) return true;
        const result = rule(input.value);
        if (result !== true) {
            box.textContent = result;
            return false;
        }
        box.textContent = '';
        return true;
    }

       form.querySelectorAll('input, textarea').forEach(input => {
        input.addEventListener('blur', () => validateField(input));
    });


    form.addEventListener('submit', (e) => {
         return;
        let ok = true;
        form.querySelectorAll('input, textarea').forEach(input => {
            if (!validateField(input)) ok = false;
        });
        if (!ok) e.preventDefault();  
    });
}
