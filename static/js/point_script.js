document.addEventListener('DOMContentLoaded', () => {
    const inputReg = document.getElementById('reg-input');
    const inputTerm = document.getElementById('term-input');
    const textContainer = document.getElementById('reg-text');

    function updateUI() {
        let amount = parseInt(inputReg.value);
        if (isNaN(amount) || amount <= 0) {
            textContainer.innerHTML = 'Введіть обсяг замовлення для розрахунку логістики.';
            return;
        }

        const truckCapacity = parseInt(inputReg.dataset.capacity);
        const speed = parseInt(inputReg.dataset.speed);
        
        let tripsPerMonth = amount / truckCapacity;
        let daysBetween = 30 / tripsPerMonth;

        let simultaneousTrucks = Math.ceil(speed / (daysBetween > 0 ? daysBetween : 1));
        if (simultaneousTrucks < 1) simultaneousTrucks = 1;

        if (daysBetween >= 1) {
            textContainer.innerHTML = `Регулярно по <span class="font-bold text-indigo-600">${truckCapacity}</span> од., кожні <mark class="bg-indigo-100 text-indigo-800 px-1 rounded font-bold">${Math.round(daysBetween)}</mark> днів.<br>
            <span class="text-xs text-slate-500 mt-2 block font-medium">Час в дорозі: ${speed} дн. | На маршруті одночасно: ${simultaneousTrucks} маш.</span>`;
        } else {
            let dailyAmount = Math.ceil(amount / 30); 
            textContainer.innerHTML = `<mark class="bg-red-100 text-red-800 px-1 rounded font-bold">ЩОДНЯ</mark> по <span class="font-bold text-indigo-600">${dailyAmount}</span> од.<br>
            <span class="text-xs text-red-500 mt-2 block font-medium">Критичне навантаження маршруту (Час: ${speed} дн.)</span>`;
        }
    }

    updateUI();

    inputReg.addEventListener('input', function() {
        this.value = this.value.replace(/\D/g, '');
        updateUI();
    });

    if (inputTerm) {
        inputTerm.addEventListener('input', function() {
            this.value = this.value.replace(/\D/g, '');
        });
    }
});