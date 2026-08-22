/*
Nombre: Andrés Peña | Maximo Perez
RUT: 22059517-K | 22104757-5
NRC: 8479
*/

const inventario = {
    "status": 200,
    "message": "Productos obtenidos correctamente",
    "data": [
        {"id": 1,"nombre": "Elden Ring", "precio": 59.99, "imagen": "https://cdn2.steamgriddb.com/thumb/557fa68027943a8b0d3b66c4e72ff23b.jpg"},
        {"id": 2,"nombre": "Persona 3", "precio": 49.99, "imagen": "https://cdn2.steamgriddb.com/thumb/7ca49777a71420e1d492a56ded84864e.jpg"},
        {"id": 3,"nombre": "Hollow Knight", "precio": 29.99, "imagen": "https://cdn2.steamgriddb.com/thumb/9122e6917c43df2c068332f00db0ff97.jpg"},
        {"id": 4,"nombre": "Metal Gear Solid 3", "precio": 39.99, "imagen": "https://cdn2.steamgriddb.com/thumb/c16af09e39c7093bd3eaa51069b0e072.jpg"},
        {"id": 5,"nombre": "Super Mario Galaxy", "precio": 19.99, "imagen": "https://cdn2.steamgriddb.com/thumb/850660ba5cb014184e5cc0e6b3d4c6bb.png"},
        {"id": 6,"nombre": "Half-Life: 3", "precio": 49.99, "imagen": "https://cdn2.steamgriddb.com/thumb/779630cd9809d73345b34a4c0d54e902.jpg"},
        {"id": 7, "nombre": "Big Walk", "precio": 19.99, "imagen": "https://cdn2.steamgriddb.com/thumb/8b23a7bae26326fdd277d8c89b78fc3b.jpg"},
        {"id": 8, "nombre": "Among Us", "precio": 4.99, "imagen": "https://cdn2.steamgriddb.com/thumb/09246ffb824ca2c5bc47a64cb302d3cb.jpg"},
        {"id": 9, "nombre": "Celeste", "precio": 19.99, "imagen": "https://cdn2.steamgriddb.com/thumb/8c433a09bd26b943147c4d9bacb15efc.jpg"},
        {"id": 10, "nombre": "Omori", "precio": 19.99, "imagen": "https://cdn2.steamgriddb.com/thumb/479371d62bb00aedb52168650b0aaeb5.jpg"},
        {"id": 11, "nombre": "Pih 2", "precio": 14.99, "imagen": "https://cdn2.steamgriddb.com/thumb/8af4b7341f432aabdb93d28d51c1d9a7.jpg"},
        {"id": 12, "nombre": "The Binding of Isaac", "precio": 14.99, "imagen": "https://cdn2.steamgriddb.com/thumb/3df344993c62fa87f02408bfbf3916a7.jpg"},
        {"id": 13, "nombre": "Terraria", "precio": 9.99, "imagen": "https://cdn2.steamgriddb.com/thumb/9bc661e8362657d8cbbe4bb41d17c7f3.jpg"},
        {"id": 14, "nombre": "Devil May Cry 3", "precio": 19.99, "imagen": "https://cdn2.steamgriddb.com/thumb/ea1da85574c351ca0a3a9e1c8bcad52c.jpg"},
        {"id": 15, "nombre": "Five Nights at Freddy's", "precio": 7.99, "imagen": "https://cdn2.steamgriddb.com/thumb/c7e30c4f80e9452d40245385c6572936.jpg"},
        {"id": 16, "nombre": "Garfield Kart", "precio": 4.99, "imagen": "https://cdn2.steamgriddb.com/thumb/a167a7fb11a219cab4406f83192b9180.jpg"},
        {"id": 17, "nombre": "Geometry Dash", "precio": 3.99, "imagen": "https://cdn2.steamgriddb.com/thumb/ca35d9a03ac12db4c2f7f5c0044e9692.jpg"},
        {"id": 18, "nombre": "Hatsune Miku: Project DIVA Mega Mix+", "precio": 39.99, "imagen": "https://cdn2.steamgriddb.com/thumb/38480a565ce050816110799f403c3c67.jpg"},
        {"id": 19, "nombre": "Super Meat Boy", "precio": 14.99, "imagen": "https://cdn2.steamgriddb.com/thumb/4e17fdfe672e908e42d1e3746afd279b.jpg"},
        {"id": 20, "nombre": "Risk of Rain 2", "precio": 24.99, "imagen": "https://cdn2.steamgriddb.com/thumb/1421d7f26f63712f41e4e46140c37180.jpg"}
        ]
};

// Variable para almacenar los productos en el carrito
let carrito = {};

// Funciones para inicializar la página y manejar el carrito de compras
function inicializarCatalogo() {
    let contenedor = document.getElementById("contenedorCatalogo");
    if (contenedor) {
        cargarCatalogo();
    }
}

// Función para inicializar la tienda y cargar los productos en el combo box
function inicializarTienda() {
    let cmb = document.getElementById("cmbJuego");
    if (cmb) {
        cmb.innerHTML = "";
        inventario.data.forEach((juego) => {
            let opt = document.createElement("option");
            opt.setAttribute("value", juego.id);
            opt.innerText = `${juego.nombre} - $${juego.precio}`;
            cmb.appendChild(opt);                    
        });
        
        actualizarTablaCarrito();
    }
}

// Función para capturar la selección del usuario y agregar el producto al carrito
function capturarYAgregar() {
    let idSeleccionado = parseInt(document.getElementById("cmbJuego").value)    ;
    let cantidadCopias = parseInt(document.getElementById("txtCantidad").value);
    
    if (cantidadCopias > 0) {
        agregarProducto(idSeleccionado, cantidadCopias);
    }
}

// Función para agregar un producto al carrito
function agregarProducto(idSeleccionado, cantidadCopias) {
    let juegoSeleccionado = inventario.data.find(j => j.id === idSeleccionado);

    let cantidadFinal = cantidadCopias;
    if (carrito[idSeleccionado]) {
        cantidadFinal = carrito[idSeleccionado].cantidad + cantidadCopias;
    }

    const itemActualizado = {
        [idSeleccionado]: {
            ...juegoSeleccionado,
            "cantidad": cantidadFinal
        }
    };

    carrito = Object.assign({}, carrito, itemActualizado);
    
    actualizarTablaCarrito();
}

// Función para eliminar un producto del carrito
function eliminarProducto(idSeleccionado) {
    if (carrito[idSeleccionado]) {
        delete carrito[idSeleccionado];

        actualizarTablaCarrito();
    }
}

// Función para calcular el total del carrito
function calcularTotal() {
    let total = 0;
    Object.values(carrito).forEach(juego => {
        total += (juego.precio * juego.cantidad);
        total.toFixed(2);
    });

    document.getElementById("lblTotal").innerText = total;
}

// Función para actualizar la tabla del carrito
function actualizarTablaCarrito() {
    let cuerpoTabla = document.getElementById("cuerpoTablaCarrito");
    cuerpoTabla.innerHTML = "";

    Object.entries(carrito).forEach(([key, value]) => {
        let subtotal = value.cantidad * value.precio;

        let fila = `
            <tr>
                <td>${value.nombre}</td>
                <td>$${value.precio.toFixed(2)}</td>
                <td>${value.cantidad}</td>
                <td>$${subtotal.toFixed(2)}</td>
                <td><button class="btn btn-danger btn-sm" onclick="eliminarProducto('${key}')">Eliminar</button></td>
            </tr>
        `;

        cuerpoTabla.innerHTML += fila;
    });

    calcularTotal();
}

// Función para cargar el catálogo de productos en la página
function cargarCatalogo() {
    let contenedorCatalogo = document.getElementById("contenedorCatalogo");
    contenedorCatalogo.innerHTML = "";

    inventario.data.forEach((juego) => {
        let col = document.createElement("div");
        col.setAttribute("class", "col-md-4 mb-4");

        let card = document.createElement("div");
        card.setAttribute("class", "p-3 card h-100");

        let imagen = document.createElement("img");
        imagen.setAttribute("src", juego.imagen);
        imagen.setAttribute("class", "card-img-top mb-3");
        imagen.setAttribute("alt", juego.nombre);

        let titulo = document.createElement("h4");
        titulo.innerText = juego.nombre;

        let precio = document.createElement("p");
        precio.setAttribute("class", "card-text text-secondary");
        precio.innerText = `$${juego.precio.toFixed(2)}`;

        card.appendChild(imagen);
        card.appendChild(titulo);
        card.appendChild(precio);

        col.appendChild(card);
        contenedorCatalogo.appendChild(col);
    });
}
