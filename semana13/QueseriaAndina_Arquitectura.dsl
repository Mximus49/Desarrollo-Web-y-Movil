workspace "QUESERIA" "Plataforma de ventas Queseria Andina" {

    // Modelo C4 de una tienda en linea de quesos artesanales.
    // C1: actores y sistema. C2: contenedores (aplicaciones y datos).
    // C3: componentes internos de los contenedores mas relevantes.
    // Ademas: vistas dinamicas (flujos de ejecucion) y vistas de despliegue.

    !identifiers hierarchical

    model {
        visitante = person "Visitante" "Persona que revisa el catalogo de quesos sin iniciar sesion."
        cliente = person "Cliente" "Persona registrada que compra quesos y revisa sus pedidos."
        administrador = person "Administrador" "Personal de la queseria que gestiona productos, stock y pedidos."

        sistema = softwareSystem "Plataforma de ventas Queseria Andina" "Sistema que permite consultar el catalogo de quesos, gestionar clientes, registrar pedidos y procesar pagos." {
            tags "SistemaEvaluado"

            frontend = container "Tienda web" "Interfaz web responsiva para visitantes, clientes y administradores." "Aplicacion web" {
                tags "Frontend"
            }

            apiGateway = container "API Gateway" "Punto de entrada unico al backend; enruta peticiones y aplica controles de acceso." "Servicio HTTP" {
                tags "Gateway"

                // C3 - Componentes internos del API Gateway.
                adaptadorHttp = component "Adaptador HTTP" "Recibe solicitudes y genera respuestas HTTP." "Modulo de entrada" {
                    tags "EntradaC3"
                }
                filtroAcceso = component "Filtro de acceso" "Distingue rutas publicas (catalogo) de rutas protegidas (pedidos, perfil)." "Modulo de seguridad" {
                    tags "ControlC3"
                }
                despachador = component "Despachador de rutas" "Dirige cada solicitud al servicio que corresponde." "Modulo de enrutamiento" {
                    tags "AplicacionC3"
                }
                traductorErrores = component "Traductor de errores" "Convierte fallos en respuestas consistentes sin revelar detalles internos." "Modulo de errores" {
                    tags "ErrorC3"
                }
            }

            authService = container "Servicio de autenticacion" "Autentica usuarios y valida sesiones." "Servicio de identidad" {
                tags "Seguridad"

                // C3 - Componentes internos del servicio de autenticacion.
                apiIdentidad = component "API de identidad" "Atiende inicio de sesion y validacion de sesiones." "API interna" {
                    tags "EntradaC3"
                }
                gestorSesiones = component "Gestor de sesiones" "Controla la vigencia de sesiones o tokens." "Servicio de identidad" {
                    tags "AplicacionC3"
                }
                verificadorCredenciales = component "Verificador de credenciales" "Comprueba credenciales sin exponer valores sensibles." "Servicio de validacion" {
                    tags "ControlC3"
                }
                repoIdentidades = component "Repositorio de identidades" "Accede a los datos de usuarios registrados." "Acceso a datos" {
                    tags "PersistenciaC3"
                }
                clienteSecretos = component "Cliente de secretos" "Obtiene claves necesarias para firmar o validar sesiones." "Adaptador de integracion" {
                    tags "IntegracionC3"
                }
            }

            secretManager = container "Administrador de secretos" "Guarda claves y credenciales y las entrega solo a servicios autorizados." "Servicio de secretos" {
                tags "Seguridad"
            }

            catalogo = container "Servicio de catalogo" "Gestiona los quesos ofrecidos, sus precios y el stock disponible." "Servicio privado" {
                tags "Privado"
            }

            pedidos = container "Servicio de pedidos" "Gestiona el ciclo de vida de los pedidos de quesos." "Servicio privado" {
                tags "Privado"

                // C3 - Componentes internos del servicio de pedidos.
                apiPedidos = component "API de pedidos" "Recibe solicitudes del gateway relacionadas con pedidos." "API interna" {
                    tags "EntradaC3"
                }
                politicaAcceso = component "Politica de acceso" "Verifica que el cliente solo opere sobre sus propios pedidos." "Reglas de autorizacion" {
                    tags "ControlC3"
                }
                idempotencia = component "Control de idempotencia" "Evita registrar dos veces el mismo pedido ante reintentos." "Regla de negocio" {
                    tags "ControlC3"
                }
                flujoPedidos = component "Servicio de pedidos" "Coordina stock, pago y cambios de estado del pedido." "Servicio de aplicacion" {
                    tags "AplicacionC3"
                }
                adaptadorCatalogo = component "Adaptador de catalogo" "Consulta o reserva stock de quesos." "Adaptador privado" {
                    tags "IntegracionC3"
                }
                adaptadorPagos = component "Adaptador de pagos" "Solicita o consulta el pago del pedido." "Adaptador privado" {
                    tags "IntegracionC3"
                }
                repoPedidos = component "Repositorio de pedidos" "Guarda pedidos y claves de operacion." "Acceso a datos" {
                    tags "PersistenciaC3"
                }
            }

            clientes = container "Servicio de clientes" "Gestiona perfiles y datos de despacho de los clientes." "Servicio privado" {
                tags "Privado"
            }

            pagos = container "Servicio de pagos" "Gestiona el estado de los pagos de cada pedido." "Servicio privado" {
                tags "Privado"
            }

            dbCatalogo = container "Datos de catalogo" "Quesos, precios y stock." "Almacen de datos" {
                tags "BaseDatos"
            }

            dbPedidos = container "Datos de pedidos" "Pedidos, estados y claves de idempotencia." "Almacen de datos" {
                tags "BaseDatos"
            }

            dbClientes = container "Datos de clientes" "Perfiles y direcciones de despacho." "Almacen de datos" {
                tags "BaseDatos"
            }

            dbPagos = container "Datos de pagos" "Estados de pago." "Almacen de datos" {
                tags "BaseDatos"
            }

            dbIdentidad = container "Datos de identidad" "Usuarios y sesiones." "Almacen de datos" {
                tags "BaseDatos"
            }

            graphqlGateway = container "GraphQL Gateway" "Permite consultas que combinan datos de varios servicios (por ejemplo, pedidos con detalle de quesos)." "Servicio GraphQL" {
                tags "Gateway"

                // C3 - Componentes internos del GraphQL Gateway.
                endpointGraphql = component "Endpoint GraphQL" "Recibe las operaciones GraphQL." "Adaptador GraphQL" {
                    tags "EntradaC3"
                }
                validadorConsultas = component "Validador de consultas" "Valida esquema y limites de complejidad." "Validacion GraphQL" {
                    tags "ControlC3"
                }
                accesoCampos = component "Politica de acceso a campos" "Comprueba permisos sobre los campos solicitados." "Modulo de autorizacion" {
                    tags "ControlC3"
                }
                resolvers = component "Resolvers" "Resuelve campos y coordina la obtencion de datos." "Resolvers GraphQL" {
                    tags "AplicacionC3"
                }
                conectores = component "Conectores de servicios" "Consulta catalogo, pedidos y clientes." "Adaptadores de integracion" {
                    tags "IntegracionC3"
                }
                compositorRespuestas = component "Compositor de respuestas" "Arma la respuesta y no presenta fallos parciales como datos completos." "Modulo de resultados" {
                    tags "ErrorC3"
                }
            }
        }

        // ---------- Relaciones C1 ----------
        visitante -> sistema "Consulta quesos disponibles"
        cliente -> sistema "Compra quesos y revisa sus pedidos"
        administrador -> sistema "Gestiona catalogo, stock y pedidos"

        // ---------- Relaciones C2 ----------
        visitante -> sistema.frontend "Revisa el catalogo" "Navegador web"
        cliente -> sistema.frontend "Compra y revisa pedidos" "Navegador web"
        administrador -> sistema.frontend "Administra la tienda" "Navegador web"
        sistema.frontend -> sistema.apiGateway "Envia solicitudes" "HTTPS"
        sistema.apiGateway -> sistema.authService "Valida identidad o sesion" "HTTPS/JSON"
        sistema.authService -> sistema.secretManager "Obtiene claves" "Canal autenticado"
        sistema.apiGateway -> sistema.catalogo "Enruta consultas del catalogo" "HTTPS/JSON"
        sistema.apiGateway -> sistema.pedidos "Enruta operaciones de pedidos" "HTTPS/JSON"
        sistema.apiGateway -> sistema.clientes "Enruta operaciones de clientes" "HTTPS/JSON"
        sistema.apiGateway -> sistema.pagos "Enruta operaciones de pagos" "HTTPS/JSON"
        sistema.apiGateway -> sistema.graphqlGateway "Enruta consultas GraphQL" "HTTPS/GraphQL"
        sistema.pagos -> sistema.secretManager "Obtiene credenciales de integracion" "Canal autenticado"
        sistema.pedidos -> sistema.catalogo "Verifica y reserva stock" "HTTPS/JSON"
        sistema.pedidos -> sistema.pagos "Solicita el pago" "HTTPS/JSON"
        sistema.catalogo -> sistema.dbCatalogo "Lee y escribe quesos y stock" "Acceso a datos"
        sistema.pedidos -> sistema.dbPedidos "Lee y escribe pedidos" "Acceso a datos"
        sistema.clientes -> sistema.dbClientes "Lee y escribe perfiles" "Acceso a datos"
        sistema.pagos -> sistema.dbPagos "Lee y escribe pagos" "Acceso a datos"
        sistema.authService -> sistema.dbIdentidad "Consulta y actualiza usuarios" "Acceso a datos"
        sistema.graphqlGateway -> sistema.catalogo "Obtiene quesos y stock" "HTTPS/JSON"
        sistema.graphqlGateway -> sistema.pedidos "Obtiene pedidos autorizados" "HTTPS/JSON"
        sistema.graphqlGateway -> sistema.clientes "Obtiene perfiles autorizados" "HTTPS/JSON"
        sistema.graphqlGateway -> sistema.authService "Comprueba identidad cuando aplica" "HTTPS/JSON"

        // ---------- Relaciones C3: API Gateway ----------
        sistema.frontend -> sistema.apiGateway.adaptadorHttp "Invoca el backend" "HTTPS"
        sistema.apiGateway.adaptadorHttp -> sistema.apiGateway.filtroAcceso "Solicita comprobacion de acceso"
        sistema.apiGateway.filtroAcceso -> sistema.authService "Valida la sesion cuando la ruta es protegida" "HTTPS/JSON"
        sistema.apiGateway.filtroAcceso -> sistema.apiGateway.despachador "Deja pasar rutas publicas o autorizadas"
        sistema.apiGateway.despachador -> sistema.catalogo "Enruta al catalogo" "HTTPS/JSON"
        sistema.apiGateway.despachador -> sistema.pedidos "Enruta a pedidos" "HTTPS/JSON"
        sistema.apiGateway.despachador -> sistema.clientes "Enruta a clientes" "HTTPS/JSON"
        sistema.apiGateway.despachador -> sistema.pagos "Enruta a pagos" "HTTPS/JSON"
        sistema.apiGateway.despachador -> sistema.graphqlGateway "Enruta consultas GraphQL" "HTTPS/GraphQL"
        sistema.apiGateway.despachador -> sistema.apiGateway.traductorErrores "Reporta fallos de comunicacion"

        // ---------- Relaciones C3: GraphQL Gateway ----------
        sistema.apiGateway -> sistema.graphqlGateway.endpointGraphql "Remite operaciones GraphQL" "HTTPS/GraphQL"
        sistema.graphqlGateway.endpointGraphql -> sistema.graphqlGateway.validadorConsultas "Verifica sintaxis y limites"
        sistema.graphqlGateway.validadorConsultas -> sistema.graphqlGateway.accesoCampos "Entrega consulta valida"
        sistema.graphqlGateway.accesoCampos -> sistema.authService "Comprueba permisos" "HTTPS/JSON"
        sistema.graphqlGateway.accesoCampos -> sistema.graphqlGateway.resolvers "Autoriza campos"
        sistema.graphqlGateway.resolvers -> sistema.graphqlGateway.conectores "Solicita datos"
        sistema.graphqlGateway.conectores -> sistema.catalogo "Consulta quesos y stock" "HTTPS/JSON"
        sistema.graphqlGateway.conectores -> sistema.pedidos "Consulta pedidos" "HTTPS/JSON"
        sistema.graphqlGateway.conectores -> sistema.clientes "Consulta perfiles" "HTTPS/JSON"
        sistema.graphqlGateway.resolvers -> sistema.graphqlGateway.compositorRespuestas "Envia datos y errores"

        // ---------- Relaciones C3: Autenticacion ----------
        sistema.apiGateway -> sistema.authService.apiIdentidad "Valida sesiones" "HTTPS/JSON"
        sistema.graphqlGateway -> sistema.authService.apiIdentidad "Consulta contexto del usuario" "HTTPS/JSON"
        sistema.authService.apiIdentidad -> sistema.authService.gestorSesiones "Gestiona sesion"
        sistema.authService.gestorSesiones -> sistema.authService.verificadorCredenciales "Verifica credenciales al iniciar sesion"
        sistema.authService.verificadorCredenciales -> sistema.authService.repoIdentidades "Consulta usuario"
        sistema.authService.repoIdentidades -> sistema.dbIdentidad "Lee datos de usuarios" "Acceso a datos"
        sistema.authService.gestorSesiones -> sistema.authService.clienteSecretos "Solicita claves"
        sistema.authService.clienteSecretos -> sistema.secretManager "Obtiene claves" "Canal autenticado"

        // ---------- Relaciones C3: Pedidos ----------
        sistema.apiGateway -> sistema.pedidos.apiPedidos "Enruta operaciones de pedidos" "HTTPS/JSON"
        sistema.graphqlGateway -> sistema.pedidos.apiPedidos "Consulta pedidos" "HTTPS/JSON"
        sistema.pedidos.apiPedidos -> sistema.pedidos.politicaAcceso "Comprueba que el pedido sea del cliente"
        sistema.pedidos.politicaAcceso -> sistema.pedidos.flujoPedidos "Permite lecturas autorizadas"
        sistema.pedidos.politicaAcceso -> sistema.pedidos.idempotencia "Permite escrituras autorizadas"
        sistema.pedidos.idempotencia -> sistema.pedidos.repoPedidos "Busca pedido previo con la misma clave"
        sistema.pedidos.idempotencia -> sistema.pedidos.flujoPedidos "Ejecuta solo pedidos nuevos"
        sistema.pedidos.flujoPedidos -> sistema.pedidos.adaptadorCatalogo "Reserva stock"
        sistema.pedidos.flujoPedidos -> sistema.pedidos.adaptadorPagos "Solicita pago"
        sistema.pedidos.flujoPedidos -> sistema.pedidos.repoPedidos "Guarda el pedido"
        sistema.pedidos.adaptadorCatalogo -> sistema.catalogo "Invoca servicio de catalogo" "HTTPS/JSON"
        sistema.pedidos.adaptadorPagos -> sistema.pagos "Invoca servicio de pagos" "HTTPS/JSON"
        sistema.pedidos.repoPedidos -> sistema.dbPedidos "Lee y escribe pedidos" "Acceso a datos"

        // ---------- Respuestas (usadas en las vistas dinamicas) ----------
        sistema.dbCatalogo -> sistema.catalogo "Devuelve quesos" "Acceso a datos"
        sistema.catalogo -> sistema.apiGateway "Responde catalogo" "HTTPS/JSON"
        sistema.apiGateway -> sistema.frontend "Devuelve respuestas o errores controlados" "HTTPS"
        sistema.frontend -> visitante "Muestra resultados" "Interfaz web"
        sistema.frontend -> cliente "Muestra resultados y errores" "Interfaz web"
        sistema.dbPedidos -> sistema.pedidos "Devuelve pedidos" "Acceso a datos"
        sistema.pedidos -> sistema.apiGateway "Responde operaciones de pedidos" "HTTPS/JSON"
        sistema.authService -> sistema.apiGateway "Responde validacion de sesion" "HTTPS/JSON"
        sistema.catalogo -> sistema.pedidos "Responde disponibilidad de stock" "HTTPS/JSON"
        sistema.pagos -> sistema.pedidos "Responde resultado del pago" "HTTPS/JSON"
        sistema.graphqlGateway -> sistema.apiGateway "Devuelve resultado agregado o error" "HTTPS/GraphQL"
        sistema.catalogo -> sistema.graphqlGateway "Devuelve quesos y stock" "HTTPS/JSON"
        sistema.pedidos -> sistema.graphqlGateway "Devuelve pedidos" "HTTPS/JSON"
        sistema.clientes -> sistema.graphqlGateway "Devuelve perfil" "HTTPS/JSON"
        sistema.graphqlGateway.validadorConsultas -> sistema.graphqlGateway.endpointGraphql "Rechaza consulta invalida"
        sistema.graphqlGateway.endpointGraphql -> sistema.apiGateway "Responde error de validacion" "HTTPS/GraphQL"
        sistema.pedidos.repoPedidos -> sistema.pedidos.idempotencia "Devuelve pedido ya registrado"
        sistema.pedidos.idempotencia -> sistema.pedidos.apiPedidos "Devuelve resultado existente"
        sistema.pedidos.apiPedidos -> sistema.apiGateway "Devuelve respuesta de pedidos" "HTTPS/JSON"

        // ---------- Despliegue: entorno de pruebas (referencial) ----------
        pruebas = deploymentEnvironment "Pruebas" {
            deploymentNode "Dispositivo del usuario" "Computador o celular con navegador." "Equipo cliente" {
                tags "ZonaCliente"
                deploymentNode "Navegador web" "Ejecuta la tienda web (SPA)." "Navegador" {
                    containerInstance sistema.frontend
                }
            }
            deploymentNode "Infraestructura de pruebas" "Agrupacion logica del entorno de pruebas." "Entorno de pruebas" {
                tags "ZonaEntorno"
                deploymentNode "Zona publica" "Unico punto expuesto hacia internet." "Segmento de acceso" {
                    tags "ZonaPublica"
                    deploymentNode "Servidor de entrada" "Ejecuta el API Gateway." "Servidor de aplicaciones" {
                        containerInstance sistema.apiGateway
                    }
                }
                deploymentNode "Zona privada" "Servicios no accesibles directamente por los usuarios." "Segmento privado" {
                    tags "ZonaPrivada"
                    deploymentNode "Servidor de servicios" "Ejecuta los servicios internos." "Host de aplicaciones" {
                        containerInstance sistema.authService
                        containerInstance sistema.graphqlGateway
                        containerInstance sistema.catalogo
                        containerInstance sistema.pedidos
                        containerInstance sistema.clientes
                        containerInstance sistema.pagos
                    }
                }
                deploymentNode "Zona de datos" "Bases de datos accesibles solo por los servicios." "Segmento de datos" {
                    tags "ZonaDatos"
                    deploymentNode "Servidor de base de datos" "Puede ser un solo motor con varios esquemas." "Servicio de datos" {
                        containerInstance sistema.dbCatalogo
                        containerInstance sistema.dbPedidos
                        containerInstance sistema.dbClientes
                        containerInstance sistema.dbPagos
                        containerInstance sistema.dbIdentidad
                    }
                }
                deploymentNode "Zona de secretos" "Gestion de claves del entorno." "Segmento protegido" {
                    tags "ZonaSecretos"
                    deploymentNode "Gestor de secretos" "No visible desde el navegador." "Servicio protegido" {
                        containerInstance sistema.secretManager
                    }
                }
            }
        }

        // ---------- Despliegue: desarrollo local ----------
        // Todo corre en un mismo equipo; la jerarquia ordena procesos, no demuestra aislamiento de red.
        local = deploymentEnvironment "Desarrollo_Local" {
            deploymentNode "Equipo de desarrollo" "Computador del desarrollador." "Estacion de trabajo" {
                tags "ZonaLocal"
                deploymentNode "Navegador local" "Tienda web en el navegador." "Navegador" {
                    containerInstance sistema.frontend
                }
                deploymentNode "Proceso de entrada" "API Gateway en un puerto local." "Proceso local" {
                    containerInstance sistema.apiGateway
                }
                deploymentNode "Procesos de servicios" "Servicios internos en procesos o contenedores." "Procesos locales" {
                    containerInstance sistema.authService
                    containerInstance sistema.graphqlGateway
                    containerInstance sistema.catalogo
                    containerInstance sistema.pedidos
                    containerInstance sistema.clientes
                    containerInstance sistema.pagos
                }
                deploymentNode "Datos y secretos locales" "Datos ficticios de quesos y claves de prueba." "Servicios locales" {
                    containerInstance sistema.dbCatalogo
                    containerInstance sistema.dbPedidos
                    containerInstance sistema.dbClientes
                    containerInstance sistema.dbPagos
                    containerInstance sistema.dbIdentidad
                    containerInstance sistema.secretManager
                }
            }
        }
    }

    views {
        // ---------- C1 ----------
        systemContext sistema "C1_Contexto" "Actores que usan la plataforma de la queseria." {
            title "C1 - Contexto de la Queseria Andina"
            include *
            autoLayout lr
        }

        // ---------- C2 ----------
        container sistema "C2_Contenedores" "Aplicaciones y almacenes de datos." {
            title "C2 - Contenedores"
            include *
            autoLayout lr
        }

        // Recortes del mismo modelo para explicar casos de uso concretos.
        container sistema "C2_Catalogo" "Contenedores que participan en la consulta del catalogo de quesos." {
            include visitante cliente sistema.frontend sistema.apiGateway sistema.authService sistema.catalogo sistema.dbCatalogo
            autoLayout lr
        }

        container sistema "C2_Pedidos" "Contenedores que participan en la compra de quesos." {
            include cliente sistema.frontend sistema.apiGateway sistema.authService sistema.pedidos sistema.catalogo sistema.pagos sistema.dbPedidos sistema.dbCatalogo sistema.dbPagos
            autoLayout lr
        }

        // ---------- C3 ----------
        component sistema.apiGateway "C3_API_Gateway" "Componentes del punto de entrada." {
            title "C3 - API Gateway"
            include *
            autoLayout lr
        }

        component sistema.graphqlGateway "C3_GraphQL" "Validacion, autorizacion y agregacion de datos." {
            title "C3 - GraphQL Gateway"
            include *
            autoLayout lr
        }

        component sistema.authService "C3_Autenticacion" "Sesiones, credenciales y secretos." {
            title "C3 - Servicio de autenticacion"
            include *
            autoLayout lr
        }

        component sistema.pedidos "C3_Pedidos" "Autorizacion, idempotencia, logica y persistencia de pedidos." {
            title "C3 - Servicio de pedidos"
            include *
            autoLayout lr
        }

        // ---------- Vistas dinamicas ----------
        dynamic sistema "D_F01_Exito" "Consulta del catalogo de quesos de punta a punta." {
            title "F01 - Consulta de catalogo: exito"
            1: visitante -> sistema.frontend "Abre el catalogo de quesos"
            2: sistema.frontend -> sistema.apiGateway "GET /quesos" "HTTPS"
            3: sistema.apiGateway -> sistema.catalogo "Consulta el catalogo" "HTTPS/JSON"
            4: sistema.catalogo -> sistema.dbCatalogo "Busca quesos publicados" "Acceso a datos"
            5: sistema.dbCatalogo -> sistema.catalogo "Devuelve quesos" "Acceso a datos"
            6: sistema.catalogo -> sistema.apiGateway "Responde listado" "HTTPS/JSON"
            7: sistema.apiGateway -> sistema.frontend "Devuelve listado" "HTTPS"
            8: sistema.frontend -> visitante "Muestra quesos o mensaje sin resultados"
            autoLayout lr
        }

        dynamic sistema "D_F01_Recuperacion" "El catalogo no responde, se informa el error y luego se recupera." {
            title "F01 - Fallo controlado y recuperacion"
            1: visitante -> sistema.frontend "Abre el catalogo"
            2: sistema.frontend -> sistema.apiGateway "GET /quesos" "HTTPS"
            3: sistema.apiGateway -> sistema.catalogo "Consulta; el servicio no responde" "HTTPS/JSON"
            4: sistema.apiGateway -> sistema.frontend "Timeout: error controlado" "HTTPS"
            5: sistema.frontend -> visitante "Muestra error sin datos falsos"
            6: visitante -> sistema.frontend "Reintenta"
            7: sistema.frontend -> sistema.apiGateway "Reintenta GET /quesos" "HTTPS"
            8: sistema.apiGateway -> sistema.catalogo "Consulta catalogo recuperado" "HTTPS/JSON"
            9: sistema.catalogo -> sistema.dbCatalogo "Busca quesos" "Acceso a datos"
            10: sistema.dbCatalogo -> sistema.catalogo "Devuelve quesos" "Acceso a datos"
            11: sistema.catalogo -> sistema.apiGateway "Responde listado" "HTTPS/JSON"
            12: sistema.apiGateway -> sistema.frontend "Devuelve listado" "HTTPS"
            13: sistema.frontend -> visitante "Muestra el catalogo"
            autoLayout lr
        }

        dynamic sistema "D_F02_Exito" "Compra de quesos con validacion de sesion, stock, pago y persistencia." {
            title "F02 - Registro de pedido: exito"
            1: cliente -> sistema.frontend "Confirma la compra del carrito"
            2: sistema.frontend -> sistema.apiGateway "POST /pedidos con clave de idempotencia" "HTTPS"
            3: sistema.apiGateway -> sistema.authService "Verifica sesion" "HTTPS/JSON"
            4: sistema.authService -> sistema.apiGateway "Sesion valida" "HTTPS/JSON"
            5: sistema.apiGateway -> sistema.pedidos "Registra pedido" "HTTPS/JSON"
            6: sistema.pedidos -> sistema.catalogo "Reserva stock de quesos" "HTTPS/JSON"
            7: sistema.catalogo -> sistema.pedidos "Confirma stock" "HTTPS/JSON"
            8: sistema.pedidos -> sistema.pagos "Procesa pago" "HTTPS/JSON"
            9: sistema.pagos -> sistema.pedidos "Confirma pago" "HTTPS/JSON"
            10: sistema.pedidos -> sistema.dbPedidos "Guarda pedido, estado y clave" "Acceso a datos"
            11: sistema.dbPedidos -> sistema.pedidos "Confirma escritura" "Acceso a datos"
            12: sistema.pedidos -> sistema.apiGateway "Devuelve numero y estado del pedido" "HTTPS/JSON"
            13: sistema.apiGateway -> sistema.frontend "Responde" "HTTPS"
            14: sistema.frontend -> cliente "Muestra confirmacion de compra"
            autoLayout lr
        }

        dynamic sistema "D_F02_Reintento" "Se reenvia el mismo pedido; no se duplica." {
            title "F02 - Reintento de pedido: sin duplicacion"
            1: cliente -> sistema.frontend "Reintenta la compra tras una respuesta incierta"
            2: sistema.frontend -> sistema.apiGateway "POST /pedidos con la misma clave" "HTTPS"
            3: sistema.apiGateway -> sistema.pedidos "Remite solicitud repetida" "HTTPS/JSON"
            4: sistema.pedidos -> sistema.dbPedidos "Busca la clave" "Acceso a datos"
            5: sistema.dbPedidos -> sistema.pedidos "Devuelve pedido ya registrado" "Acceso a datos"
            6: sistema.pedidos -> sistema.apiGateway "Reutiliza resultado, no crea otro pedido" "HTTPS/JSON"
            7: sistema.apiGateway -> sistema.frontend "Devuelve el mismo numero de pedido" "HTTPS"
            8: sistema.frontend -> cliente "Muestra el pedido existente"
            autoLayout lr
        }

        dynamic sistema.pedidos "D_F02_Idempotencia_C3" "Detalle interno de un pedido repetido." {
            title "F02 - Idempotencia: componentes"
            1: sistema.apiGateway -> sistema.pedidos.apiPedidos "Entrega POST repetido y clave" "HTTPS/JSON"
            2: sistema.pedidos.apiPedidos -> sistema.pedidos.politicaAcceso "Verifica permisos"
            3: sistema.pedidos.politicaAcceso -> sistema.pedidos.idempotencia "Permite escritura"
            4: sistema.pedidos.idempotencia -> sistema.pedidos.repoPedidos "Busca la clave"
            5: sistema.pedidos.repoPedidos -> sistema.dbPedidos "Consulta pedido guardado" "Acceso a datos"
            6: sistema.pedidos.repoPedidos -> sistema.pedidos.idempotencia "Entrega pedido existente"
            7: sistema.pedidos.idempotencia -> sistema.pedidos.apiPedidos "Retorna sin ejecutar el flujo"
            8: sistema.pedidos.apiPedidos -> sistema.apiGateway "Devuelve el mismo pedido" "HTTPS/JSON"
            autoLayout lr
        }

        dynamic sistema "D_F03_Propio" "El cliente consulta un pedido suyo." {
            title "F03 - Consulta de pedido propio"
            1: cliente -> sistema.frontend "Abre uno de sus pedidos"
            2: sistema.frontend -> sistema.apiGateway "GET /pedidos/id" "HTTPS"
            3: sistema.apiGateway -> sistema.authService "Comprueba sesion" "HTTPS/JSON"
            4: sistema.authService -> sistema.apiGateway "Sesion valida" "HTTPS/JSON"
            5: sistema.apiGateway -> sistema.pedidos "Solicita pedido con identidad del cliente" "HTTPS/JSON"
            6: sistema.pedidos -> sistema.dbPedidos "Consulta filtrando por cliente" "Acceso a datos"
            7: sistema.dbPedidos -> sistema.pedidos "Devuelve el pedido" "Acceso a datos"
            8: sistema.pedidos -> sistema.apiGateway "Responde datos autorizados" "HTTPS/JSON"
            9: sistema.apiGateway -> sistema.frontend "Devuelve pedido" "HTTPS"
            10: sistema.frontend -> cliente "Muestra detalle y estado"
            autoLayout lr
        }

        dynamic sistema "D_F03_Ajeno" "El cliente intenta ver un pedido de otra persona." {
            title "F03 - Consulta de pedido ajeno"
            1: cliente -> sistema.frontend "Intenta abrir pedido de otro cliente"
            2: sistema.frontend -> sistema.apiGateway "GET /pedidos/idAjeno" "HTTPS"
            3: sistema.apiGateway -> sistema.authService "Comprueba sesion" "HTTPS/JSON"
            4: sistema.authService -> sistema.apiGateway "Sesion valida (no implica acceso al pedido)" "HTTPS/JSON"
            5: sistema.apiGateway -> sistema.pedidos "Consulta con identidad del cliente" "HTTPS/JSON"
            6: sistema.pedidos -> sistema.dbPedidos "Consulta filtrando por cliente" "Acceso a datos"
            7: sistema.dbPedidos -> sistema.pedidos "No encuentra pedido autorizado" "Acceso a datos"
            8: sistema.pedidos -> sistema.apiGateway "Rechaza sin revelar el pedido" "HTTPS/JSON"
            9: sistema.apiGateway -> sistema.frontend "Entrega error" "HTTPS"
            10: sistema.frontend -> cliente "Muestra rechazo sin datos ajenos"
            autoLayout lr
        }

        dynamic sistema "D_F03_Expirada" "El gateway rechaza antes de llegar al servicio de pedidos." {
            title "F03 - Sesion expirada"
            1: cliente -> sistema.frontend "Consulta pedido con sesion expirada"
            2: sistema.frontend -> sistema.apiGateway "GET /pedidos/id" "HTTPS"
            3: sistema.apiGateway -> sistema.authService "Verifica sesion" "HTTPS/JSON"
            4: sistema.authService -> sistema.apiGateway "Sesion expirada" "HTTPS/JSON"
            5: sistema.apiGateway -> sistema.frontend "Responde rechazo de autenticacion" "HTTPS"
            6: sistema.frontend -> cliente "Pide iniciar sesion nuevamente"
            autoLayout lr
        }

        dynamic sistema "D_F04_GraphQL_Exito" "Vista de 'Mis pedidos' con el detalle de cada queso." {
            title "F04 - GraphQL: agregacion exitosa"
            1: cliente -> sistema.frontend "Abre Mis pedidos"
            2: sistema.frontend -> sistema.apiGateway "POST /graphql" "HTTPS"
            3: sistema.apiGateway -> sistema.graphqlGateway "Entrega consulta y contexto" "HTTPS/GraphQL"
            4: sistema.graphqlGateway -> sistema.catalogo "Consulta detalle de quesos" "HTTPS/JSON"
            4: sistema.graphqlGateway -> sistema.pedidos "Consulta pedidos del cliente" "HTTPS/JSON"
            5: sistema.catalogo -> sistema.graphqlGateway "Devuelve quesos" "HTTPS/JSON"
            5: sistema.pedidos -> sistema.graphqlGateway "Devuelve pedidos" "HTTPS/JSON"
            6: sistema.graphqlGateway -> sistema.apiGateway "Compone respuesta" "HTTPS/GraphQL"
            7: sistema.apiGateway -> sistema.frontend "Entrega resultado" "HTTPS"
            8: sistema.frontend -> cliente "Muestra pedidos con detalle de quesos"
            autoLayout lr
        }

        dynamic sistema "D_F04_GraphQL_Parcial" "Un servicio falla y no se muestra informacion incompleta como si fuera completa." {
            title "F04 - GraphQL: dependencia fallida"
            1: cliente -> sistema.frontend "Abre Mis pedidos"
            2: sistema.frontend -> sistema.apiGateway "POST /graphql" "HTTPS"
            3: sistema.apiGateway -> sistema.graphqlGateway "Remite consulta" "HTTPS/GraphQL"
            4: sistema.graphqlGateway -> sistema.catalogo "Consulta quesos" "HTTPS/JSON"
            4: sistema.graphqlGateway -> sistema.pedidos "Consulta pedidos (falla)" "HTTPS/JSON"
            5: sistema.catalogo -> sistema.graphqlGateway "Devuelve quesos" "HTTPS/JSON"
            5: sistema.pedidos -> sistema.graphqlGateway "Devuelve error controlado" "HTTPS/JSON"
            6: sistema.graphqlGateway -> sistema.apiGateway "Entrega error o respuesta parcial marcada" "HTTPS/GraphQL"
            7: sistema.apiGateway -> sistema.frontend "Transmite el error" "HTTPS"
            8: sistema.frontend -> cliente "Informa que la informacion esta incompleta"
            autoLayout lr
        }

        dynamic sistema.graphqlGateway "D_F04_GraphQL_Limite_C3" "Consulta demasiado compleja rechazada antes de llegar a los servicios." {
            title "F04 - GraphQL: consulta excede limite"
            1: sistema.apiGateway -> sistema.graphqlGateway.endpointGraphql "Envia consulta excesiva" "HTTPS/GraphQL"
            2: sistema.graphqlGateway.endpointGraphql -> sistema.graphqlGateway.validadorConsultas "Calcula complejidad"
            3: sistema.graphqlGateway.validadorConsultas -> sistema.graphqlGateway.endpointGraphql "Rechaza consulta"
            4: sistema.graphqlGateway.endpointGraphql -> sistema.apiGateway "Devuelve error sin ejecutar resolvers" "HTTPS/GraphQL"
            autoLayout lr
        }

        // ---------- Vistas de despliegue ----------
        deployment sistema pruebas "DEP_Pruebas" "Ubicacion de aplicaciones y datos en el entorno de pruebas." {
            title "Despliegue - Pruebas (referencial)"
            include *
            autoLayout lr
        }

        deployment sistema local "DEP_Local" "Todos los servicios en un equipo local." {
            title "Despliegue - Desarrollo local"
            include *
            autoLayout lr
        }

        styles {
            // Despliegue
            element "Deployment Node" {
                background #F3EEE3
                color #4A3B1F
                stroke #B8A47A
            }
            element "ZonaCliente" {
                background #FBF7EE
                color #4A3B1F
            }
            element "ZonaEntorno" {
                background #F7F3EA
                color #4A3B1F
            }
            element "ZonaPublica" {
                background #FCEFC7
                color #5C4410
            }
            element "ZonaPrivada" {
                background #E5EEE8
                color #20513D
            }
            element "ZonaDatos" {
                background #ECEAF2
                color #463D64
            }
            element "ZonaSecretos" {
                background #EEE5E1
                color #68483C
            }
            element "ZonaLocal" {
                background #F5F1E8
                color #4A3B1F
            }

            // C1 y C2
            element "Person" {
                shape person
                background #8A6A2F
                color #FFFFFF
            }
            element "Software System" {
                shape roundedbox
                background #B8860B
                color #FFFFFF
            }
            element "SistemaEvaluado" {
                background #9C6F12
                color #FFFFFF
            }
            element "Container" {
                shape roundedbox
                background #FFF4D6
                color #4A3B1F
            }
            element "Frontend" {
                shape webbrowser
                background #FFE9A8
                color #4A3B1F
            }
            element "Gateway" {
                background #C99A2E
                color #FFFFFF
            }
            element "Seguridad" {
                background #6B5A3A
                color #FFFFFF
            }
            element "Privado" {
                background #FAEBC0
                color #4A3B1F
            }
            element "BaseDatos" {
                shape cylinder
                background #EFE6D2
                color #4A3B1F
            }

            // C3
            element "Component" {
                shape roundedbox
                background #FFF8E6
                color #4A3B1F
            }
            element "EntradaC3" {
                background #FFE9A8
                color #4A3B1F
            }
            element "ControlC3" {
                background #EDE3CF
                color #4A3B1F
            }
            element "AplicacionC3" {
                background #D7E9DE
                color #20533E
            }
            element "IntegracionC3" {
                background #E9E2F2
                color #4A3666
            }
            element "PersistenciaC3" {
                background #E9EBEE
                color #334454
            }
            element "ErrorC3" {
                background #F2E6DB
                color #70462C
            }
            relationship "Relationship" {
                color #7A6A4F
                thickness 2
            }
        }
    }
}
