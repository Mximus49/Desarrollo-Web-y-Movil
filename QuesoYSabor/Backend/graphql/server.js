const express = require('express');
const crypto = require('crypto');
const fs = require('fs');
const https = require('https');
const path = require('path');
const { ApolloServer, gql } = require('apollo-server-express');
const { GraphQLError } = require('graphql');

// GraphQL Gateway privado de Queso & Sabor.
// No lee ninguna base de datos: junta datos llamando a las APIs de orders, inventory y analytics.
// Escucha con TLS y solo acepta llamadas del API Gateway (clave de servicio graphql).
// No toca bases de datos de otros servicios y no tiene mutations: las reglas de negocio
// se quedan en cada servicio.

const VAULT_ADDR = (process.env.VAULT_ADDR || 'https://127.0.0.1:8200').replace(/\/$/, '');
const VAULT_TOKEN = process.env.VAULT_TOKEN;
const CERTS = process.env.CERTS_DIR || path.join(__dirname, '..', 'certs');
const URLS = {
    orders: process.env.ORDERS_URL || 'https://127.0.0.1:9002',
    inventory: process.env.INVENTORY_URL || 'https://127.0.0.1:9001',
    analytics: process.env.ANALYTICS_URL || 'https://127.0.0.1:9005'
};
const PROFUNDIDAD_MAXIMA = 5;
const CAMPOS_MAXIMOS = 60;
const LARGO_MAXIMO = 3000;
const ROLES_STOCK = ['admin', 'dueno'];

if (!VAULT_TOKEN) {
    throw new Error('VAULT_TOKEN no esta configurado');
}

const claves = {};

async function leerClave(servicio) {
    const res = await fetch(`${VAULT_ADDR}/v1/secret/data/quesoysabor/${servicio}`, {
        headers: { 'X-Vault-Token': VAULT_TOKEN },
        signal: AbortSignal.timeout(5000)
    });
    if (!res.ok) {
        throw new Error(`No fue posible leer la clave de ${servicio} desde Vault`);
    }
    const datos = await res.json();
    return datos.data.data.service_key;
}

const typeDefs = gql`
    type Producto {
        id: ID!
        nombre: String!
        categoria: String!
        precioFinal: Int!
        disponible: Boolean!
        "Solo admin y dueno"
        stock: Int
    }
    type Linea {
        nombre: String!
        cantidad: Int!
        precioUnitario: Int!
        subtotal: Int!
        producto: Producto
    }
    type Boleta {
        folio: Int!
        neto: Int!
        iva: Int!
        total: Int!
    }
    type ResumenPedido {
        id: ID!
        estado: String!
        modalidad: String!
        total: Int!
        creado: String!
        boleta: Boleta
        lineas: [Linea!]!
    }
    type ProductoVendido {
        productId: ID!
        nombre: String!
        unidades: Int!
        monto: Int!
    }
    type Ventas {
        pedidosPagados: Int!
        totalVendido: Int!
        ticketPromedio: Int!
        productosMasVendidos: [ProductoVendido!]!
    }
    type Panel {
        ventas: Ventas
        productosBajoStock(limite: Int = 5): [Producto!]
    }
    type Query {
        resumenPedido(id: ID!): ResumenPedido
        misPedidos(limite: Int = 10): [ResumenPedido!]!
        panelAdmin: Panel
    }
`;

// Llama a un servicio interno con su clave y la identidad que verifico el API Gateway.
// Asi orders sigue revisando por su cuenta que el pedido sea del usuario.
async function llamar(ctx, servicio, ruta) {
    let res;
    try {
        res = await fetch(`${URLS[servicio]}${ruta}`, {
            headers: { 'X-Service-Key': claves[servicio], ...ctx.identidad },
            signal: AbortSignal.timeout(4000)
        });
    } catch (err) {
        throw new GraphQLError(`${servicio} no disponible`);
    }
    if (res.status === 404) return null;
    if (res.status === 403) throw new GraphQLError('No autorizado');
    if (!res.ok) throw new GraphQLError(`${servicio} respondio ${res.status}`);
    return res.json();
}

// Junta los ids de productos de toda la consulta y los pide a inventory en una sola llamada,
// en vez de hacer una llamada por cada linea del pedido.
function crearCargadorProductos(ctx) {
    const cache = new Map();
    return async function cargar(ids) {
        const faltan = [...new Set(ids)].filter(id => !cache.has(id));
        if (faltan.length > 0) {
            const pedido = llamar(ctx, 'inventory', `/products?ids=${encodeURIComponent(faltan.join(','))}`)
                .then(lista => new Map((lista || []).map(p => [p.id, p])));
            faltan.forEach(id => cache.set(id, pedido.then(mapa => mapa.get(id) || null)));
        }
        return Promise.all(ids.map(id => cache.get(id)));
    };
}

function pedidoAResumen(p) {
    return {
        id: p.id,
        estado: p.estado,
        modalidad: p.modalidad,
        total: p.total,
        creado: p.creado,
        boleta: p.boleta,
        lineas: p.items.map(i => ({
            nombre: i.nombre,
            cantidad: i.cantidad,
            precioUnitario: i.precio_unitario,
            subtotal: i.subtotal,
            productId: i.product_id
        }))
    };
}

function productoGraphql(p) {
    return {
        id: p.id,
        nombre: p.nombre,
        categoria: p.categoria,
        precioFinal: p.precio_final,
        disponible: p.disponible,
        stock: p.stock
    };
}

const resolvers = {
    Query: {
        async resumenPedido(obj, { id }, ctx) {
            const pedido = await llamar(ctx, 'orders', `/orders/${encodeURIComponent(id)}`);
            if (pedido == null) {
                throw new GraphQLError('Pedido no encontrado');
            }
            return pedidoAResumen(pedido);
        },
        async misPedidos(obj, { limite }, ctx) {
            const tope = Math.min(Math.max(limite, 1), 20);
            const pedidos = await llamar(ctx, 'orders', `/orders/mine?limit=${tope}`);
            const resumenes = (pedidos || []).map(pedidoAResumen);
            // Se precargan todos los productos de una vez
            ctx.cargarProductos(resumenes.flatMap(r => r.lineas.map(l => l.productId))).catch(() => null);
            return resumenes;
        },
        panelAdmin(obj, args, ctx) {
            if (!ctx.roles.some(r => ROLES_STOCK.includes(r))) {
                throw new GraphQLError('No autorizado');
            }
            return {};
        }
    },
    Linea: {
        // Si inventory no responde, el pedido igual se muestra y producto queda en null con un error
        async producto(linea, args, ctx) {
            const [producto] = await ctx.cargarProductos([linea.productId]);
            return producto ? productoGraphql(producto) : null;
        }
    },
    Producto: {
        stock(producto, args, ctx) {
            if (!ctx.roles.some(r => ROLES_STOCK.includes(r))) {
                throw new GraphQLError('No autorizado para ver el stock');
            }
            return producto.stock ?? null;
        }
    },
    Panel: {
        async ventas(obj, args, ctx) {
            const v = await llamar(ctx, 'analytics', '/analytics/ventas');
            return {
                pedidosPagados: v.pedidos_pagados,
                totalVendido: v.total_vendido,
                ticketPromedio: v.ticket_promedio,
                productosMasVendidos: v.productos_mas_vendidos.map(p => ({
                    productId: p.product_id, nombre: p.nombre, unidades: p.unidades, monto: p.monto
                }))
            };
        },
        async productosBajoStock(obj, { limite }, ctx) {
            const lista = await llamar(ctx, 'inventory', `/admin/products?bajo_stock=${Math.max(limite, 0)}`);
            return (lista || []).map(productoGraphql);
        }
    }
};

// Regla de validacion propia: rechaza consultas muy profundas o con demasiados campos
// antes de ejecutar cualquier resolver.
function limitesConsulta(context) {
    function medir(selectionSet, nivel, visitados) {
        let profundidad = nivel;
        let campos = 0;
        for (const sel of selectionSet.selections) {
            let sub = null;
            if (sel.kind === 'Field') {
                campos += 1;
                if (sel.selectionSet) sub = medir(sel.selectionSet, nivel + 1, visitados);
            } else if (sel.kind === 'InlineFragment') {
                sub = medir(sel.selectionSet, nivel, visitados);
            } else if (sel.kind === 'FragmentSpread' && !visitados.has(sel.name.value)) {
                const fragmento = context.getFragment(sel.name.value);
                if (fragmento) sub = medir(fragmento.selectionSet, nivel, new Set([...visitados, sel.name.value]));
            }
            if (sub) {
                profundidad = Math.max(profundidad, sub.profundidad);
                campos += sub.campos;
            }
        }
        return { profundidad, campos };
    }
    return {
        OperationDefinition(node) {
            const { profundidad, campos } = medir(node.selectionSet, 1, new Set());
            if (profundidad > PROFUNDIDAD_MAXIMA) {
                context.reportError(new GraphQLError(`Consulta demasiado profunda (${profundidad}), maximo ${PROFUNDIDAD_MAXIMA}`));
            }
            if (campos > CAMPOS_MAXIMOS) {
                context.reportError(new GraphQLError(`Consulta con demasiados campos (${campos}), maximo ${CAMPOS_MAXIMOS}`));
            }
        }
    };
}

function verificarGateway(req, res, next) {
    const recibida = Buffer.from(req.get('X-Service-Key') || '');
    const esperada = Buffer.from(claves.graphql);
    if (recibida.length !== esperada.length || !crypto.timingSafeEqual(recibida, esperada)) {
        return res.status(403).json({ detail: 'Llamada no autorizada' });
    }
    next();
}

async function startServer() {
    for (const servicio of ['graphql', 'orders', 'inventory', 'analytics']) {
        claves[servicio] = await leerClave(servicio);
    }

    const app = express();
    app.get('/health', verificarGateway, (req, res) => res.json({ status: 'OK', service: 'GraphQL Gateway' }));
    app.use('/graphql', verificarGateway, express.json({ limit: '10kb' }), (req, res, next) => {
        if (typeof req.body?.query !== 'string' || req.body.query.length > LARGO_MAXIMO) {
            return res.status(400).json({ detail: 'Consulta ausente o demasiado larga' });
        }
        next();
    });

    const apolloServer = new ApolloServer({
        typeDefs,
        resolvers,
        introspection: false,
        // Sin stacktrace en los errores, para no mostrar rutas ni detalles internos
        debug: false,
        validationRules: [limitesConsulta],
        context: ({ req }) => {
            // Identidad que puso el API Gateway despues de validar el token
            const ctx = {
                roles: (req.get('X-Authenticated-Roles') || '').split(',').filter(Boolean),
                identidad: {
                    'X-Authenticated-User-Id': req.get('X-Authenticated-User-Id') || '',
                    'X-Authenticated-User': req.get('X-Authenticated-User') || '',
                    'X-Authenticated-Roles': req.get('X-Authenticated-Roles') || ''
                }
            };
            ctx.cargarProductos = crearCargadorProductos(ctx);
            return ctx;
        }
    });
    await apolloServer.start();
    apolloServer.applyMiddleware({ app, path: '/graphql', cors: false });

    // Solo escucha en la maquina local y con TLS: desde afuera se llega por el API Gateway
    const tls = {
        key: fs.readFileSync(path.join(CERTS, 'servidor.key')),
        cert: fs.readFileSync(path.join(CERTS, 'servidor.crt'))
    };
    https.createServer(tls, app).listen(8090, '127.0.0.1', () => {
        console.log('GraphQL Gateway iniciado en https://127.0.0.1:8090/graphql');
    });
}

startServer().catch(err => {
    console.error(err.message);
    process.exit(1);
});
