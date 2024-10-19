ymaps.ready(init);

let userMarkers = {};

function init() {
    const map = new ymaps.Map("map", {
        center: [42.460341, 59.617996],
        zoom: 14,
        controls: ['zoomControl', 'geolocationControl'],
        theme: "dark"
    });

    const placemark = new ymaps.Placemark([55.751244, 37.618423], {
        balloonContent: `
                    <div>
                        <h3>Центр Москвы</h3>
                        <p>Добро пожаловать в Москву!</p>
                        <a href="https://www.mos.ru" target="_blank">Перейти на сайт Москвы</a>
                    </div>
                `
    }, {
        preset: 'islands#blueCircleDotIcon'
    });

    map.geoObjects.add(placemark);

    const socket = new WebSocket('ws://192.168.100.8:8000/ws/map/');

    socket.onopen = function (event) {
        console.log("WebSocket connected.");
    };

    socket.onmessage = function (event) {
        const data = JSON.parse(event.data);

        if (data.type === "location_update") {
            const userId = data.user_id;
            const username = data.username;
            const first_name = data.first_name;
            const last_name = data.last_name;
            const car_number = data.car_number;
            const phone_number = data.phone_number;
            const latitude = data.latitude;
            const longitude = data.longitude;

            console.log(data);

            if (userMarkers[userId]) {
                userMarkers[userId].geometry.setCoordinates([latitude, longitude]);
            } else {
                const placemark = new ymaps.Placemark([latitude, longitude], {
                    balloonContent: `
                    <div>
                        <p class="text-blue-400 font-bold">${first_name} ${last_name}</p>
                        <p class="text-black font-medium">Гос. номер: ${car_number}</p>
                        <p class="text-black font-medium">Номер телефона: ${phone_number}</p>
                    </div>
                    `
                }, {
                    preset: 'islands#circleIcon',
                    iconColor: '#769FCD',
                });

                userMarkers[userId] = placemark;
                map.geoObjects.add(placemark);
            }
        }
    };

    socket.onclose = function (event) {
        console.log("WebSocket закрыт.");
    };

    socket.onerror = function (error) {
        console.error("WebSocket ошибка: ", error);
    };
}