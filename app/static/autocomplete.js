document.addEventListener('DOMContentLoaded', function() {
    const input = document.querySelector('input[name="city"]');
    if (!input) return;

    let datalist = document.getElementById('cities-list');
    if (!datalist) {
        datalist = document.createElement('datalist');
        datalist.id = 'cities-list';
        document.body.appendChild(datalist);
    }
    input.setAttribute('list', 'cities-list');

    input.addEventListener('input', function() {
        const value = input.value.trim();
        if (value.length === 0) {
            datalist.innerHTML = '';
            return;
        }
        fetch('/api/autocomplete?q=' + encodeURIComponent(value))
            .then(r => r.json())
            .then(data => {
                datalist.innerHTML = '';
                data.forEach(city => {
                    const option = document.createElement('option');
                    option.value = city;
                    datalist.appendChild(option);
                });
            });
    });
});