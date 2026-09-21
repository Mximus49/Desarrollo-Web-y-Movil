<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Quesería Andina - Locales</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,500;0,9..144,600;1,9..144,500&family=Work+Sans:wght@400;500;600&display=swap" rel="stylesheet">
  <link href="index.css" rel="stylesheet">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css">
</head>
<body>

<header class="topbar">
  <div class="logo">Quesería Andina <span>desde 1978</span></div>
  <div class="search">
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
    <input type="text" placeholder="Buscar quesos, quesillos, tablas…">
  </div>
  <div class="auth-actions">
    <a href="#" class="btn-login">Iniciar sesión</a>
    <a href="#" class="btn-register">Registrarse</a>
  </div>
</header>

<nav class="mainnav">
  <ul>
    <li><a href="index.php">Inicio</a></li>
    <li><a href="catalogo.php">Catálogo</a></li>
    <li><a href="Ofertas.php">Ofertas</a></li>
    <li class="active"><a href="Locales.php">Locales</a></li>
    <li><a href="Contacto.php">Contacto</a></li>
    <li class="nav-right">
      <a href="Carrito.php">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/><path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/></svg>
        <span>Carrito</span>
        <span class="cart-count"></span>
      </a>
    </li>
  </ul>
</nav>

<div class="locales-layout">
  <div>
    <h1 style="margin-bottom:22px;">Nuestros locales</h1>

    <div class="locale-card" data-lat="-33.4263" data-lng="-70.6109" data-nombre="Local Providencia">
      <h4>Local Providencia</h4>
      <div class="meta">
        Av. Los Conquistadores 1234, Providencia<br>
        +56 9 1234 5678<br>
        Lun a sáb, 9:00 a 20:00
      </div>
    </div>

    <div class="locale-card" data-lat="-33.4569" data-lng="-70.5985" data-nombre="Local Ñuñoa">
      <h4>Local Ñuñoa</h4>
      <div class="meta">
        Av. Irarrázaval 3200, Ñuñoa<br>
        +56 9 2345 6789<br>
        Lun a sáb, 9:30 a 19:30
      </div>
    </div>

    <div class="locale-card" data-lat="-33.4104" data-lng="-70.5720" data-nombre="Local Las Condes">
      <h4>Local Las Condes</h4>
      <div class="meta">
        Av. Apoquindo 4500, Las Condes<br>
        +56 9 3456 7890<br>
        Lun a sáb, 10:00 a 21:00
      </div>
    </div>
  </div>

  <div id="map"></div>
</div>

<footer>
  <div>
    <h3>Quesería Andina</h3>
    <p class="desc">Afinamos y distribuimos quesos artesanales del sur de Chile desde 1978, directo de la cava a tu mesa.</p>
  </div>
  <div>
    <h3>Contacto</h3>
    <ul>
      <li><a href="Contacto.php">contacto@queseriaandina.cl</a></li>
      <li><a href="Contacto.php">+56 9 1234 5678</a></li>
      <li><a href="Locales.php">Nuestros locales</a></li>
    </ul>
  </div>
  <div>
    <h3>Nosotros</h3>
    <ul>
      <li><a href="#">Nuestra historia</a></li>
      <li><a href="#">Productores</a></li>
      <li><a href="#">Trabaja con nosotros</a></li>
    </ul>
  </div>
  <div class="foot-bottom">© 2026 Quesería Andina. Todos los derechos reservados.</div>
</footer>

<script src="app.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js"></script>
<script>
  document.addEventListener('DOMContentLoaded', function () {
    var mapEl = document.getElementById('map');
    if (!mapEl || typeof L === 'undefined') return;

    var map = L.map('map').setView([-33.4372, -70.5930], 12);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
      maxZoom: 18
    }).addTo(map);

    var cards = document.querySelectorAll('.locale-card');
    var markers = {};

    cards.forEach(function (card) {
      var lat = parseFloat(card.getAttribute('data-lat'));
      var lng = parseFloat(card.getAttribute('data-lng'));
      var nombre = card.getAttribute('data-nombre');
      var marker = L.marker([lat, lng]).addTo(map).bindPopup(nombre);
      markers[nombre] = marker;

      card.addEventListener('click', function () {
        cards.forEach(function (c) { c.classList.remove('is-active'); });
        card.classList.add('is-active');
        map.flyTo([lat, lng], 15, { duration: 0.6 });
        marker.openPopup();
      });

      marker.on('click', function () {
        cards.forEach(function (c) { c.classList.remove('is-active'); });
        card.classList.add('is-active');
      });
    });
  });
</script>
</body>
</html>