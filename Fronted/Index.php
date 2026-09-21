<<<<<<< HEAD:Fronted/index.php
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Queso y Sabor - Inicio</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,500;0,9..144,600;1,9..144,500&family=Work+Sans:wght@400;500;600&display=swap" rel="stylesheet">
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
  <link href="index.css" rel="stylesheet">
</head>
<body>

<header class="topbar">
  <div class="logo">Queso Y Sabor<span>desde 1978</span></div>
  <div class="search">
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
    <input type="text" placeholder="Buscar quesos, quesillos, tablas…">
  </div>
  <div class="d-flex align-items-center gap-2">
    <button type="button" class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#loginModal">
      Iniciar sesión
    <button type="button" class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#RegisterModal">
      Registrarse
  </div>
</header>

  <div class="modal fade" id="loginModal" tabindex="-1" aria-labelledby="loginModalLabel" aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title" id="loginModalLabel">Iniciar Sesión</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Cerrar"></button>
        </div>
        <form action="#" method="POST">
          <div class="modal-body">
            <div class="mb-3">
              <label for="login-email" class="form-label">Correo electrónico</label>
              <input type="email" class="form-control" id="login-email" placeholder="nombre@ejemplo.cl" required>
            </div>
            <div class="mb-3">
              <label for="login-password" class="form-label">Contraseña</label>
              <input type="password" class="form-control" id="login-password" placeholder="Tu contraseña" required>
            </div>
            <div class="d-flex justify-content-between align-items-center">
              <div class="form-check">
                <input type="checkbox" class="form-check-input" id="recordarme">
                <label class="form-check-label small" for="recordarme">Recordarme</label>
              </div>
              <a href="#" class="small text-decoration-none">¿Olvidaste tu contraseña?</a>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
            <button type="submit" class="btn btn-primary">Ingresar</button>
          </div>
        </form>
      </div>
    </div>
  </div>

  <div class="modal fade" id="RegisterModal" tabindex="-1" aria-labelledby="loginModalLabel" aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title" id="loginModalLabel">Resgitro</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Cerrar"></button>
        </div>
        <form action="#" method="POST">
          <div class="modal-body">
            <div class="mb-3">
              <label for="login-email" class="form-label">Correo electrónico</label>
              <input type="email" class="form-control" id="login-email" placeholder="nombre@ejemplo.cl" required>
            </div>
            <div class="mb-3">
              <label for="Name" class="form-label">Nombre</label>
              <input type="email" class="form-control" id="login-email" placeholder="nombre@ejemplo.cl" required>
            </div>
            <div class="mb-3">
              <label for="Create-Password" class="form-label">Contraseña</label>
              <input type="password" class="form-control" id="login-password" placeholder="Tu contraseña" required>
            </div>
            <div class="mb-3">
              <label for="Create-Password" class="form-label">Repita la contraseña</label>
              <input type="password" class="form-control" id="login-password" placeholder="Tu contraseña" required>
            </div>
            <div class="d-flex justify-content-between align-items-center">
              <div class="form-check">
                <input type="checkbox" class="form-check-input" id="recordarme">
                <label class="form-check-label small" for="recordarme">Recordarme</label>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
            <button type="submit" class="btn btn-primary">Registrarse</button>
          </div>
        </form>
      </div>
    </div>
  </div>

<nav class="mainnav">
  <ul>
    <li class="active"><a href="index.php">Inicio</a></li>
    <li><a href="catalogo.php">Catálogo</a></li>
    <li><a href="Ofertas.php">Ofertas</a></li>
    <li><a href="Locales.php">Locales</a></li>
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

<main>
  <section class="hero">
    <div class="hero-art">
      <svg viewBox="0 0 480 420" xmlns="http://www.w3.org/2000/svg">
        <ellipse cx="240" cy="390" rx="190" ry="18" fill="rgba(74,17,25,0.08)"/>
        <g>
          <ellipse cx="200" cy="330" rx="150" ry="34" fill="#D9B15C"/>
          <rect x="50" y="290" width="300" height="40" fill="#E8C471"/>
          <ellipse cx="200" cy="290" rx="150" ry="34" fill="#F1D38C"/>
          <ellipse cx="200" cy="290" rx="150" ry="34" fill="none" stroke="#C79A45" stroke-width="2" stroke-dasharray="3 6"/>
        </g>
        <g>
          <ellipse cx="170" cy="248" rx="118" ry="28" fill="#8B5E34"/>
          <rect x="52" y="212" width="236" height="36" fill="#A9754A"/>
          <ellipse cx="170" cy="212" rx="118" ry="28" fill="#C79465"/>
        </g>
        <g>
          <path d="M120 212 Q170 150 260 190 L260 212 Z" fill="#EFE4C1"/>
          <path d="M120 212 Q170 150 260 190" fill="none" stroke="#C79465" stroke-width="4" stroke-linecap="round"/>
          <circle cx="165" cy="196" r="4" fill="#D9B15C"/>
          <circle cx="185" cy="204" r="3" fill="#D9B15C"/>
          <circle cx="200" cy="192" r="3.5" fill="#D9B15C"/>
        </g>
        <g>
          <path d="M250 300 L340 250 L360 340 L280 360 Z" fill="#F3EFE4"/>
          <path d="M250 300 L340 250 L360 340 L280 360 Z" fill="none" stroke="#8B5E34" stroke-width="3"/>
          <g stroke="#5B6B6E" stroke-width="1.4" opacity="0.6">
            <path d="M270 305 q20 8 10 30"/>
            <path d="M295 292 q18 14 6 40"/>
            <path d="M315 282 q14 20 -2 46"/>
          </g>
        </g>
        <path d="M60 300 Q90 320 60 340" fill="none" stroke="#4A1119" stroke-width="2" opacity="0.5"/>
      </svg>

      <svg class="seal" viewBox="0 0 120 120">
        <circle cx="60" cy="60" r="56" fill="#6E1F2B"/>
        <circle cx="60" cy="60" r="56" fill="none" stroke="#E4C580" stroke-width="2" stroke-dasharray="2 4"/>
        <text x="60" y="52" text-anchor="middle" fill="#F5EEDC" font-family="Fraunces, serif" font-size="15" font-weight="600">Oferta</text>
        <text x="60" y="70" text-anchor="middle" fill="#E4C580" font-family="Work Sans, sans-serif" font-size="10">de temporada</text>
        <text x="60" y="86" text-anchor="middle" fill="#F5EEDC" font-family="Fraunces, serif" font-size="13">-20%</text>
      </svg>
    </div>

    <div class="hero-copy">
      <div class="eyebrow-line">Selección de otoño</div>
      <h1>El queso madura en la cava, no en la fábrica.</h1>
      <p>Traemos directo de las queserías del sur productos afinados a mano, en pequeños lotes, con la misma receta desde 1978.</p>
      <div class="hero-actions">
        <a href="Ofertas.php" class="btn-primary">Ver selección de temporada</a>
        <a href="Locales.php" class="btn-ghost">Encuentra tu local</a>
      </div>
    </div>
  </section>

  <aside class="featured">
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
    <a href="catalogo.php" class="see-all">Ver todo el catálogo</a>
  </aside>
</main>

<footer>
  <div>
    <h3>Queso Y Sabor</h3>
    <p class="desc">Afinamos y distribuimos quesos artesanales del sur de Chile desde 1978, directo de la cava a tu mesa.</p>
  </div>
  <div>
    <h3>Contacto</h3>
    <ul>
      <li><a href="Contacto.php">contacto@quesoysabor.cl</a></li>
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
  <div class="foot-bottom">© 2026 Queso Y Sabor. Todos los derechos reservados.</div>
</footer>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
<script src="app.js"></script>
</body>
=======
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Quesería Andina - Inicio</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,500;0,9..144,600;1,9..144,500&family=Work+Sans:wght@400;500;600&display=swap" rel="stylesheet">
  <link href="index.css" rel="stylesheet">
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
    <li class="active"><a href="index.php">Inicio</a></li>
    <li><a href="catalogo.php">Catálogo</a></li>
    <li><a href="Ofertas.php">Ofertas</a></li>
    <li><a href="Locales.php">Locales</a></li>
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

<main>
  <section class="hero">
    <div class="hero-art">
      <svg viewBox="0 0 480 420" xmlns="http://www.w3.org/2000/svg">
        <ellipse cx="240" cy="390" rx="190" ry="18" fill="rgba(74,17,25,0.08)"/>
        <g>
          <ellipse cx="200" cy="330" rx="150" ry="34" fill="#D9B15C"/>
          <rect x="50" y="290" width="300" height="40" fill="#E8C471"/>
          <ellipse cx="200" cy="290" rx="150" ry="34" fill="#F1D38C"/>
          <ellipse cx="200" cy="290" rx="150" ry="34" fill="none" stroke="#C79A45" stroke-width="2" stroke-dasharray="3 6"/>
        </g>
        <g>
          <ellipse cx="170" cy="248" rx="118" ry="28" fill="#8B5E34"/>
          <rect x="52" y="212" width="236" height="36" fill="#A9754A"/>
          <ellipse cx="170" cy="212" rx="118" ry="28" fill="#C79465"/>
        </g>
        <g>
          <path d="M120 212 Q170 150 260 190 L260 212 Z" fill="#EFE4C1"/>
          <path d="M120 212 Q170 150 260 190" fill="none" stroke="#C79465" stroke-width="4" stroke-linecap="round"/>
          <circle cx="165" cy="196" r="4" fill="#D9B15C"/>
          <circle cx="185" cy="204" r="3" fill="#D9B15C"/>
          <circle cx="200" cy="192" r="3.5" fill="#D9B15C"/>
        </g>
        <g>
          <path d="M250 300 L340 250 L360 340 L280 360 Z" fill="#F3EFE4"/>
          <path d="M250 300 L340 250 L360 340 L280 360 Z" fill="none" stroke="#8B5E34" stroke-width="3"/>
          <g stroke="#5B6B6E" stroke-width="1.4" opacity="0.6">
            <path d="M270 305 q20 8 10 30"/>
            <path d="M295 292 q18 14 6 40"/>
            <path d="M315 282 q14 20 -2 46"/>
          </g>
        </g>
        <path d="M60 300 Q90 320 60 340" fill="none" stroke="#4A1119" stroke-width="2" opacity="0.5"/>
      </svg>

      <svg class="seal" viewBox="0 0 120 120">
        <circle cx="60" cy="60" r="56" fill="#6E1F2B"/>
        <circle cx="60" cy="60" r="56" fill="none" stroke="#E4C580" stroke-width="2" stroke-dasharray="2 4"/>
        <text x="60" y="52" text-anchor="middle" fill="#F5EEDC" font-family="Fraunces, serif" font-size="15" font-weight="600">Oferta</text>
        <text x="60" y="70" text-anchor="middle" fill="#E4C580" font-family="Work Sans, sans-serif" font-size="10">de temporada</text>
        <text x="60" y="86" text-anchor="middle" fill="#F5EEDC" font-family="Fraunces, serif" font-size="13">-20%</text>
      </svg>
    </div>

    <div class="hero-copy">
      <div class="eyebrow-line">Selección de otoño</div>
      <h1>El queso madura en la cava, no en la fábrica.</h1>
      <p>Traemos directo de las queserías del sur productos afinados a mano, en pequeños lotes, con la misma receta desde 1978.</p>
      <div class="hero-actions">
        <a href="Ofertas.php" class="btn-primary">Ver selección de temporada</a>
        <a href="Locales.php" class="btn-ghost">Encuentra tu local</a>
      </div>
    </div>
  </section>

  <aside class="featured">
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
    <a href="catalogo.php" class="see-all">Ver todo el catálogo</a>
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
</body>
>>>>>>> 7d8877a20574ac0133592c173dc3c414d3ca0906:Fronted/Index.php
</html>