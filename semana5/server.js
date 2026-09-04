const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const {ApolloServer, gql} = require('apollo-server-express');

const Usario = require('./models/usuario');

mongoose.connect('mongodb://localhost:27017/quesoysabor_usuarios');

const typeDefs = gql`
    type Usuario {
        id: ID!
        run: String!
        nombreCompleto: String!
        direccion: String!
        comuna: String!
        provincia: String!
        region: String!
        fechaNacimiento: String!
        sexo: String!
        correo: String!
        telefono: String!
        pass: String!
        perfil: String!
        correoValidado: Boolean!
    }

    input UsuarioInput {
        run: String!
        nombreCompleto: String!
        direccion: String!
        comuna: String!
        provincia: String!
        region: String!
        fechaNacimiento: String!
        sexo: String!
        correo: String!
        telefono: String!
        pass: String!
        perfil: String!
    }
    type Alert{
        message: String!
    }
    type Query {
        getUsuarios: [Usuario]
        getUsuarioByID(id: ID!): Usuario
    }
    type Mutation {
        addUsuario(input: UsuarioInput): Usuario
        updUsuario(id: ID!, input: UsuarioInput): Usuario
        delUsuario(id: ID!): Alert
    }
`;

const resolvers = {
    Query: {
        async getUsuarios(obj){
            const usuarios = await Usario.find();
            return usuarios;
        },
        async getUsuarioByID(obj, {id}){
            const usuarioBus = await Usario.findById(id);
            if (usuarioBus == null){
                return null;
            } else {
                return usuarioBus;
            }
        } 
    },
    Mutation: {
        async addUsuario(obj, {input}){
            const usuario = new Usario({...input, correoValidado: false});
            await usuario.save();
            return usuario;
        },
        async updUsuario(obj, {id, input}){
            const usuario = await Usario.findByIdAndUpdate(id, input, {new: true});
            return usuario;
        },
        async delUsuario(obj, {id}){
            await Usuario.deleteOne({_id: id});
            return {
                message: 'Usuario eliminado'
            }
        }
    }
};

let apolloServer = null;
const corsOptions = {
    origin: '*',
    credentials: false
};

async function startServer() {
    const app = express();
    app.use(cors(corsOptions));

    apolloServer = new ApolloServer({typeDefs, resolvers, cors: corsOptions});
    await apolloServer.start();
    
    apolloServer.applyMiddleware({app, cors: corsOptions});

    app.listen(8090, function () {
        console.log('API GraphQL Queso & Sabor iniciada en http://localhost:8090/graphql');
    });
}


startServer();

