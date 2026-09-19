<!DOCTYPE html>
<html lang="es">
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Quesería Andina — Inicio</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="index.css" rel="stylesheet">
<body>

<header class="topbar">
  <div class="logo">Quesería Andina <span>desde 1978</span></div>
  <div class="search">
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
    <input type="text" placeholder="Buscar quesos, quesillos, tablas…">
  </div>
  <a href="#" class="account">
    <span>Ingresar</span>
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"/><polyline points="10 17 15 12 10 7"/><line x1="15" y1="12" x2="3" y2="12"/></svg>
  </a>
</header>

<nav class="mainnav">
  <ul>
    <li class="active"><a href="index.php">Inicio</a></li>
    <li><a href="catalogo.php">Catálogo</a></li>
    <li><a href="Ofertas.php">Ofertas</a></li>
    <li><a href="Locales.php">Locales</a></li>
    <li><a href="Contacto.php">Contacto</a></li>
    <li class="nav-right">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/><path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/></svg>
      <span>Carrito</span>
      <span class="cart-count"></span>
    </li>
  </ul>
</nav>

<main>
  <section class="hero">
    <div class="hero-art">
      <!-- stacked cheese wheels, drawn as SVG so the hero is grounded in the subject -->
      <svg viewBox="0 0 480 420" xmlns="http://www.w3.org/2000/svg">
        <ellipse cx="240" cy="390" rx="190" ry="18" fill="rgba(74,17,25,0.08)"/>
        <!-- bottom wheel: mantecoso -->
        <g>
          <ellipse cx="200" cy="330" rx="150" ry="34" fill="#D9B15C"/>
          <rect x="50" y="290" width="300" height="40" fill="#E8C471"/>
          <ellipse cx="200" cy="290" rx="150" ry="34" fill="#F1D38C"/>
          <ellipse cx="200" cy="290" rx="150" ry="34" fill="none" stroke="#C79A45" stroke-width="2" stroke-dasharray="3 6"/>
        </g>
        <!-- middle wheel: rind cheese -->
        <g>
          <ellipse cx="170" cy="248" rx="118" ry="28" fill="#8B5E34"/>
          <rect x="52" y="212" width="236" height="36" fill="#A9754A"/>
          <ellipse cx="170" cy="212" rx="118" ry="28" fill="#C79465"/>
        </g>
        <!-- top wedge cut showing pale interior -->
        <g>
          <path d="M120 212 Q170 150 260 190 L260 212 Z" fill="#EFE4C1"/>
          <path d="M120 212 Q170 150 260 190" fill="none" stroke="#C79465" stroke-width="4" stroke-linecap="round"/>
          <circle cx="165" cy="196" r="4" fill="#D9B15C"/>
          <circle cx="185" cy="204" r="3" fill="#D9B15C"/>
          <circle cx="200" cy="192" r="3.5" fill="#D9B15C"/>
        </g>
        <!-- small blue-veined wedge, front -->
        <g>
          <path d="M250 300 L340 250 L360 340 L280 360 Z" fill="#F3EFE4"/>
          <path d="M250 300 L340 250 L360 340 L280 360 Z" fill="none" stroke="#8B5E34" stroke-width="3"/>
          <g stroke="#5B6B6E" stroke-width="1.4" opacity="0.6">
            <path d="M270 305 q20 8 10 30"/>
            <path d="M295 292 q18 14 6 40"/>
            <path d="M315 282 q14 20 -2 46"/>
          </g>
        </g>
        <!-- twine -->
        <path d="M60 300 Q90 320 60 340" fill="none" stroke="#4A1119" stroke-width="2" opacity="0.5"/>
      </svg>

      <svg class="seal" viewBox="0 0 120 120">
        <circle cx="60" cy="60" r="56" fill="#6E1F2B"/>
        <circle cx="60" cy="60" r="56" fill="none" stroke="#E4C580" stroke-width="2" stroke-dasharray="2 4"/>
        <text x="60" y="52" text-anchor="middle" fill="#F5EEDC" font-family="Fraunces, serif" font-size="15" font-weight="600">Oferta</text>
        <text x="60" y="70" text-anchor="middle" fill="#E4C580" font-family="Work Sans, sans-serif" font-size="10">de temporada</text>
        <text x="60" y="86" text-anchor="middle" fill="#F5EEDC" font-family="Fraunces, serif" font-size="13">−20%</text>
      </svg>
    </div>

    <div class="hero-copy">
      <div class="eyebrow-line">Selección de otoño</div>
      <h1>El queso madura en la cava, no en la fábrica.</h1>
      <p>Traemos directo de las queserías del sur productos afinados a mano, en pequeños lotes, con la misma receta desde 1978.</p>
      <div class="hero-actions">
        <button class="btn-primary">Ver selección de temporada</button>
        <a href="#" class="btn-ghost">Encuentra tu local</a>
      </div>
    </div>
  </section>

  <aside>
    <h2>Destacados esta semana</h2>
    <div class="product-list">

      <div class="product-card">
        <div class="product-thumb">
          <svg viewBox="0 0 60 60"><circle cx="30" cy="30" r="28" fill="#E8C471"/><circle cx="30" cy="30" r="28" fill="none" stroke="#C79A45" stroke-width="2"/><circle cx="22" cy="24" r="3" fill="#D9B15C"/><circle cx="36" cy="30" r="2.4" fill="#D9B15C"/><circle cx="28" cy="38" r="2.8" fill="#D9B15C"/></svg>
        </div>
        <div class="product-info">
          <div class="name">Mantecoso Añejo</div>
          <div class="meta">Pieza · 900 g aprox.</div>
        </div>
        <div class="product-price">$6.990</div>
      </div>

      <div class="product-card">
        <div class="product-thumb">
          <svg viewBox="0 0 60 60"><circle cx="30" cy="30" r="28" fill="#B9722F"/><circle cx="30" cy="30" r="28" fill="none" stroke="#8B5E34" stroke-width="2"/><circle cx="30" cy="30" r="20" fill="#D89A55"/><circle cx="30" cy="30" r="20" fill="none" stroke="#8B5E34" stroke-width="1"/></svg>
        </div>
        <div class="product-info">
          <div class="name">Chanco Ahumado</div>
          <div class="meta">Pieza · 750 g aprox.</div>
        </div>
        <div class="product-price">$5.490</div>
      </div>

      <div class="product-card">
        <div class="product-thumb">
          <svg viewBox="0 0 60 60"><circle cx="30" cy="30" r="28" fill="#F3EFE4"/><circle cx="30" cy="30" r="28" fill="none" stroke="#8B5E34" stroke-width="2"/><path d="M14 24q16 -10 32 0" stroke="#5B6B6E" stroke-width="1.3" fill="none" opacity="0.55"/><path d="M12 32q18 8 36 0" stroke="#5B6B6E" stroke-width="1.3" fill="none" opacity="0.55"/></svg>
        </div>
        <div class="product-info">
          <div class="name">Reserva de Cabra</div>
          <div class="meta">Pieza · 400 g aprox.</div>
        </div>
        <div class="product-price">$7.290</div>
      </div>

    </div>
    <a href="#" class="see-all">Ver todo el catálogo</a>
  </aside>
</main>

<footer>
  <div>
    <h3>Quesería Andina</h3>
    <p class="desc">Afinamos y distribuimos quesos artesanales del sur de Chile desde 1978, directo de la cava a tu mesa.</p>
  </div>
  <div>
    <h3>Contacto</h3>
    <ul>
      <li><a href="#">contacto@queseriaandina.cl</a></li>
      <li><a href="#">+56 9 1234 5678</a></li>
      <li><a href="#">Nuestros locales</a></li>
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

</body>
</html>