const mongoose = require('mongoose');

// run, nombre completo, direccion, comuna, provincia, region, fecha de nacimeinto, sexo, correo electronico, telefono, correovalidado, perfil

const usuarioSchema = mongoose.Schema({
    run: String,
    nombreCompleto: String,
    direccion: String,
    comuna: String,
    provincia: String,
    region: String,
    fechaNacimiento: String,
    sexo: String,
    correo: String,
    telefono: String,
    pass: String,
    perfil: {type: String, enum: ['admin', 'usuario','cajero'], default: 'usuario'},
    correoValidado: {type: Boolean, default: false}
});

module.exports = mongoose.model('Usuario', usuarioSchema);