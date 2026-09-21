<<<<<<< HEAD
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Queso Y Sabor - Ofertas</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,500;0,9..144,600;1,9..144,500&family=Work+Sans:wght@400;500;600&display=swap" rel="stylesheet">
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
  <link href="index.css" rel="stylesheet">
</head>
<body>

<header class="topbar">
  <div class="logo">Queso Y Sabor <span>desde 1978</span></div>
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
    <li><a href="index.php">Inicio</a></li>
    <li><a href="catalogo.php">Catálogo</a></li>
    <li class="active"><a href="Ofertas.php">Ofertas</a></li>
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

<div class="page-layout">
  <div class="page-title">
    <h1>Ofertas de temporada</h1>
    <p>Selección con descuento, mientras dure el stock.</p>
  </div>

  <aside class="filters">
    <h3>Filtros</h3>
    <form id="filter-form">
      <fieldset class="filter-group">
        <legend>Tipo de queso</legend>
        <label class="filter-option">
          <input type="checkbox" value="madurado"> Madurados
        </label>
        <label class="filter-option">
          <input type="checkbox" value="especial"> Especiales
        </label>
      </fieldset>
      <button type="submit" class="btn-filter">Aplicar filtros</button>
      <a href="#" class="filter-reset">Limpiar filtros</a>
    </form>
  </aside>

  <section class="product-grid">

    <div class="product-card-lg" data-category="madurado">
      <svg class="badge-offer" viewBox="0 0 64 64"><polygon points="32,2 38,14 51,10 47,23 60,28 47,33 51,46 38,42 32,54 26,42 13,46 17,33 4,28 17,23 13,10 26,14" fill="#6E1F2B"/><text x="32" y="30" text-anchor="middle" fill="#F5EEDC" font-family="Fraunces, serif" font-weight="600" font-size="13">-15%</text><text x="32" y="42" text-anchor="middle" fill="#E4C580" font-family="Work Sans, sans-serif" font-size="8">OFERTA</text></svg>
      <div class="art">
        <svg viewBox="0 0 120 120"><circle cx="60" cy="60" r="54" fill="#E8C471"/><circle cx="60" cy="60" r="54" fill="none" stroke="#C79A45" stroke-width="3"/><circle cx="44" cy="46" r="6" fill="#D9B15C"/><circle cx="72" cy="58" r="5" fill="#D9B15C"/><circle cx="56" cy="76" r="5.5" fill="#D9B15C"/></svg>
      </div>
      <h4>Mantecoso Añejo</h4>
      <div class="price-row">
        <span class="price-now">$5.940</span>
        <span class="price-old">$6.990</span>
      </div>
      <button class="btn-add" data-add-to-cart data-id="mantecoso-anejo-oferta" data-name="Mantecoso Añejo (oferta)" data-price="5940">Agregar al carro</button>
    </div>

    <div class="product-card-lg" data-category="madurado">
      <svg class="badge-offer" viewBox="0 0 64 64"><polygon points="32,2 38,14 51,10 47,23 60,28 47,33 51,46 38,42 32,54 26,42 13,46 17,33 4,28 17,23 13,10 26,14" fill="#6E1F2B"/><text x="32" y="30" text-anchor="middle" fill="#F5EEDC" font-family="Fraunces, serif" font-weight="600" font-size="13">-20%</text><text x="32" y="42" text-anchor="middle" fill="#E4C580" font-family="Work Sans, sans-serif" font-size="8">OFERTA</text></svg>
      <div class="art">
        <svg viewBox="0 0 120 120"><circle cx="60" cy="60" r="54" fill="#B9722F"/><circle cx="60" cy="60" r="54" fill="none" stroke="#8B5E34" stroke-width="3"/><circle cx="60" cy="60" r="38" fill="#D89A55"/><circle cx="60" cy="60" r="38" fill="none" stroke="#8B5E34" stroke-width="1.5"/></svg>
      </div>
      <h4>Chanco Ahumado</h4>
      <div class="price-row">
        <span class="price-now">$4.390</span>
        <span class="price-old">$5.490</span>
      </div>
      <button class="btn-add" data-add-to-cart data-id="chanco-ahumado-oferta" data-name="Chanco Ahumado (oferta)" data-price="4390">Agregar al carro</button>
    </div>

    <div class="product-card-lg" data-category="madurado">
      <svg class="badge-offer" viewBox="0 0 64 64"><polygon points="32,2 38,14 51,10 47,23 60,28 47,33 51,46 38,42 32,54 26,42 13,46 17,33 4,28 17,23 13,10 26,14" fill="#6E1F2B"/><text x="32" y="30" text-anchor="middle" fill="#F5EEDC" font-family="Fraunces, serif" font-weight="600" font-size="13">-10%</text><text x="32" y="42" text-anchor="middle" fill="#E4C580" font-family="Work Sans, sans-serif" font-size="8">OFERTA</text></svg>
      <div class="art">
        <svg viewBox="0 0 120 120"><path d="M30 90 L90 30 L100 96 Z" fill="#F1D38C"/><path d="M30 90 L90 30 L100 96 Z" fill="none" stroke="#8B5E34" stroke-width="3"/><path d="M40 84 q30 -30 55 -46" stroke="#C79A45" stroke-width="2" fill="none" stroke-dasharray="2 5"/></svg>
      </div>
      <h4>Manchego Reserva</h4>
      <div class="price-row">
        <span class="price-now">$8.010</span>
        <span class="price-old">$8.900</span>
      </div>
      <button class="btn-add" data-add-to-cart data-id="manchego-reserva-oferta" data-name="Manchego Reserva (oferta)" data-price="8010">Agregar al carro</button>
    </div>

    <div class="product-card-lg" data-category="especial">
      <svg class="badge-offer" viewBox="0 0 64 64"><polygon points="32,2 38,14 51,10 47,23 60,28 47,33 51,46 38,42 32,54 26,42 13,46 17,33 4,28 17,23 13,10 26,14" fill="#6E1F2B"/><text x="32" y="30" text-anchor="middle" fill="#F5EEDC" font-family="Fraunces, serif" font-weight="600" font-size="13">-25%</text><text x="32" y="42" text-anchor="middle" fill="#E4C580" font-family="Work Sans, sans-serif" font-size="8">OFERTA</text></svg>
      <div class="art">
        <svg viewBox="0 0 120 120"><path d="M28 92 L92 34 L104 96 Z" fill="#F3EFE4"/><path d="M28 92 L92 34 L104 96 Z" fill="none" stroke="#8B5E34" stroke-width="3"/><g stroke="#5B6B6E" stroke-width="1.6" opacity="0.6"><path d="M46 86 q18 8 8 -26"/><path d="M64 78 q16 12 4 -34"/><path d="M80 70 q12 18 -2 -40"/></g></svg>
      </div>
      <h4>Azul Andino</h4>
      <div class="price-row">
        <span class="price-now">$7.120</span>
        <span class="price-old">$9.490</span>
      </div>
      <button class="btn-add" data-add-to-cart data-id="azul-andino-oferta" data-name="Azul Andino (oferta)" data-price="7120">Agregar al carro</button>
    </div>

    <p class="empty-state" id="empty-state">No hay ofertas que coincidan con los filtros seleccionados.</p>

  </section>
</div>

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
  <title>Quesería Andina - Ofertas</title>
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
    <li><a href="index.php">Inicio</a></li>
    <li><a href="catalogo.php">Catálogo</a></li>
    <li class="active"><a href="Ofertas.php">Ofertas</a></li>
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

<div class="page-layout">
  <div class="page-title">
    <h1>Ofertas de temporada</h1>
    <p>Selección con descuento, mientras dure el stock.</p>
  </div>

  <aside class="filters">
    <h3>Filtros</h3>
    <form id="filter-form">
      <fieldset class="filter-group">
        <legend>Tipo de queso</legend>
        <label class="filter-option">
          <input type="checkbox" value="madurado"> Madurados
        </label>
        <label class="filter-option">
          <input type="checkbox" value="especial"> Especiales
        </label>
      </fieldset>
      <button type="submit" class="btn-filter">Aplicar filtros</button>
      <a href="#" class="filter-reset">Limpiar filtros</a>
    </form>
  </aside>

  <section class="product-grid">

    <div class="product-card-lg" data-category="madurado">
      <svg class="badge-offer" viewBox="0 0 64 64"><polygon points="32,2 38,14 51,10 47,23 60,28 47,33 51,46 38,42 32,54 26,42 13,46 17,33 4,28 17,23 13,10 26,14" fill="#6E1F2B"/><text x="32" y="30" text-anchor="middle" fill="#F5EEDC" font-family="Fraunces, serif" font-weight="600" font-size="13">-15%</text><text x="32" y="42" text-anchor="middle" fill="#E4C580" font-family="Work Sans, sans-serif" font-size="8">OFERTA</text></svg>
      <div class="art">
        <svg viewBox="0 0 120 120"><circle cx="60" cy="60" r="54" fill="#E8C471"/><circle cx="60" cy="60" r="54" fill="none" stroke="#C79A45" stroke-width="3"/><circle cx="44" cy="46" r="6" fill="#D9B15C"/><circle cx="72" cy="58" r="5" fill="#D9B15C"/><circle cx="56" cy="76" r="5.5" fill="#D9B15C"/></svg>
      </div>
      <h4>Mantecoso Añejo</h4>
      <div class="price-row">
        <span class="price-now">$5.940</span>
        <span class="price-old">$6.990</span>
      </div>
      <button class="btn-add" data-add-to-cart data-id="mantecoso-anejo-oferta" data-name="Mantecoso Añejo (oferta)" data-price="5940">Agregar al carro</button>
    </div>

    <div class="product-card-lg" data-category="madurado">
      <svg class="badge-offer" viewBox="0 0 64 64"><polygon points="32,2 38,14 51,10 47,23 60,28 47,33 51,46 38,42 32,54 26,42 13,46 17,33 4,28 17,23 13,10 26,14" fill="#6E1F2B"/><text x="32" y="30" text-anchor="middle" fill="#F5EEDC" font-family="Fraunces, serif" font-weight="600" font-size="13">-20%</text><text x="32" y="42" text-anchor="middle" fill="#E4C580" font-family="Work Sans, sans-serif" font-size="8">OFERTA</text></svg>
      <div class="art">
        <svg viewBox="0 0 120 120"><circle cx="60" cy="60" r="54" fill="#B9722F"/><circle cx="60" cy="60" r="54" fill="none" stroke="#8B5E34" stroke-width="3"/><circle cx="60" cy="60" r="38" fill="#D89A55"/><circle cx="60" cy="60" r="38" fill="none" stroke="#8B5E34" stroke-width="1.5"/></svg>
      </div>
      <h4>Chanco Ahumado</h4>
      <div class="price-row">
        <span class="price-now">$4.390</span>
        <span class="price-old">$5.490</span>
      </div>
      <button class="btn-add" data-add-to-cart data-id="chanco-ahumado-oferta" data-name="Chanco Ahumado (oferta)" data-price="4390">Agregar al carro</button>
    </div>

    <div class="product-card-lg" data-category="madurado">
      <svg class="badge-offer" viewBox="0 0 64 64"><polygon points="32,2 38,14 51,10 47,23 60,28 47,33 51,46 38,42 32,54 26,42 13,46 17,33 4,28 17,23 13,10 26,14" fill="#6E1F2B"/><text x="32" y="30" text-anchor="middle" fill="#F5EEDC" font-family="Fraunces, serif" font-weight="600" font-size="13">-10%</text><text x="32" y="42" text-anchor="middle" fill="#E4C580" font-family="Work Sans, sans-serif" font-size="8">OFERTA</text></svg>
      <div class="art">
        <svg viewBox="0 0 120 120"><path d="M30 90 L90 30 L100 96 Z" fill="#F1D38C"/><path d="M30 90 L90 30 L100 96 Z" fill="none" stroke="#8B5E34" stroke-width="3"/><path d="M40 84 q30 -30 55 -46" stroke="#C79A45" stroke-width="2" fill="none" stroke-dasharray="2 5"/></svg>
      </div>
      <h4>Manchego Reserva</h4>
      <div class="price-row">
        <span class="price-now">$8.010</span>
        <span class="price-old">$8.900</span>
      </div>
      <button class="btn-add" data-add-to-cart data-id="manchego-reserva-oferta" data-name="Manchego Reserva (oferta)" data-price="8010">Agregar al carro</button>
    </div>

    <div class="product-card-lg" data-category="especial">
      <svg class="badge-offer" viewBox="0 0 64 64"><polygon points="32,2 38,14 51,10 47,23 60,28 47,33 51,46 38,42 32,54 26,42 13,46 17,33 4,28 17,23 13,10 26,14" fill="#6E1F2B"/><text x="32" y="30" text-anchor="middle" fill="#F5EEDC" font-family="Fraunces, serif" font-weight="600" font-size="13">-25%</text><text x="32" y="42" text-anchor="middle" fill="#E4C580" font-family="Work Sans, sans-serif" font-size="8">OFERTA</text></svg>
      <div class="art">
        <svg viewBox="0 0 120 120"><path d="M28 92 L92 34 L104 96 Z" fill="#F3EFE4"/><path d="M28 92 L92 34 L104 96 Z" fill="none" stroke="#8B5E34" stroke-width="3"/><g stroke="#5B6B6E" stroke-width="1.6" opacity="0.6"><path d="M46 86 q18 8 8 -26"/><path d="M64 78 q16 12 4 -34"/><path d="M80 70 q12 18 -2 -40"/></g></svg>
      </div>
      <h4>Azul Andino</h4>
      <div class="price-row">
        <span class="price-now">$7.120</span>
        <span class="price-old">$9.490</span>
      </div>
      <button class="btn-add" data-add-to-cart data-id="azul-andino-oferta" data-name="Azul Andino (oferta)" data-price="7120">Agregar al carro</button>
    </div>

    <p class="empty-state" id="empty-state">No hay ofertas que coincidan con los filtros seleccionados.</p>

  </section>
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
</body>
>>>>>>> 7d8877a20574ac0133592c173dc3c414d3ca0906
</html>