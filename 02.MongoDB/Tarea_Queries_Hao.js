/****************************** IMPORTACIÓN **********************************/
/****************************************************************************/
// Conteo de registros importandos.
db.crimes.count()

// Cardinalidad de los campos.
db.crimes.distinct('location').length

// Determinar si hay duplicados por "dr_no".
db.crimes.aggregate([
    {$group: {
        _id: "$dr_no",
        count: {$sum: 1}
    }},
    {$match: {count: {$gt: 1}}}
]).count()

// Revisando los valores de los documentos duplicados (todos campos son iguales)
db.crimes.find({dr_no: "201208887"})

// Con la ayuda de CHATGPT: eliminar docs duplicados.
const bulkOps = []

db.crimes.aggregate([
  {
    $group: {
      _id: "$dr_no",
      uniqueIds: { $addToSet: "$_id" },
      count: { $sum: 1 }
    }
  },
  {
    $match: {
      count: { $gt: 1 }
    }
  }
]).forEach(function (doc) {
  doc.uniqueIds.shift()
  bulkOps.push({
    deleteOne: {
      filter: { _id: { $in: doc.uniqueIds } }
    }
  })
})

if (bulkOps.length > 0) {
  db.crimes.bulkWrite(bulkOps)
}

/************************** MODIFICACIÓN Y CREACIÓN **************************/
/****************************************************************************/
// Tipo de los campos
db.crimes.find({}).limit(1)

// Crear una nueva colección con solamente los campos de interés,
//además con todos los cambios necesarios hechos.
db.crimes.aggregate([
    {$addFields: {
        "victim.age": {$toInt: "$vict_age"},
        "victim.sex": "$vict_sex",
        "victim.descent": "$vict_descent",
        "MOcodes": {$split: ["$mocodes", " "]},
        "time": {$concat: [{$substr: ["$time_occ", 0, 2]}, ":", {$substr: ["$time_occ", 2, 2]}]},
        "date_reported": {$toDate: "$date_rptd"},
        "date_occ": {$toDate: "$date_occ"}

    }},
    {$addFields: {
        "date_occurrence": {$toDate: {$concat: [{$substr: ["$date_occ", 0, 10]}, "T", "$time", ":00"]}}
    }},
    {$project: {
        "_id": false,
        "date_occurrence": true,
        "date_occ": true,
        "date_reported": true,
        "area_name": true,
        "status_desc": true,
        "crm_cd_desc": true,
        "part_1_2": true,
        "MOcodes": true,
        "weapon_desc": true,
        "premis_desc": true,
        "victim.age": true,
        "victim.sex": true,
        "victim.descent": true
    }},
    {$out: "crimes_modificado"}
])

// Ejemplo de comparación.
db.crimes.find({}).limit(1)

db.crimes_modificado.find({}).limit(1)

/****************************** ANÁLISIS ******************************************/
/*********************************************************************************/

/******************* Dimension Temporal ************************/
// En total hay 826312 docs.
db.crimes_modificado.count()

// Por año en el que ocurrió.
db.crimes_modificado.aggregate([
    {$group: {
        _id: {
            año: {$year: "$date_occurrence"}
        },
        count: {$sum: 1}
    }},
    {$sort: {_id: 1}}
])

// Por año y mes de ocurrencia.
db.crimes_modificado.aggregate([
    {$group: {
        _id: {
            año: {$year: "$date_occurrence"},
            mes: {$month: "$date_occurrence"}
        },
        count: {$sum: 1}
    }},
    {$sort: {_id: 1}}
])

// Por hora de ocurrencia.
db.crimes_modificado.aggregate([
    {$group: {
        _id: {
            hora: {$hour: "$date_occurrence"}
        },
        count: {$sum: 1}
    }},
    {$project: {
        _id: true,
        count: true,
        percent: {$multiply:[{$divide: ["$count", 826312]}, 100]}
    }},
    {$sort: {_id: 1}}
])

// Por hora de ocurrencia.
db.crimes_modificado.aggregate([
    {$group: {
        _id: {
            hora: {$hour: "$date_occurrence"}
        },
        count: {$sum: 1}
    }},
    {$project: {
        _id: true,
        count: true,
        percent: {$multiply:[{$divide: ["$count", 826312]}, 100]}
    }},
    {$sort: {_id: 1}}
])

// Tendencia central de los días de retraso de la denuncia con respecto a la ocurrencia del delito.
// Hay 8,6400,000 milisegundos en un día.
db.crimes_modificado.aggregate([
    {$addFields: {
        rpt_delay_days: {$divide: [{$subtract: ["$date_reported", "$date_occ"]}, 86400000]}
    }},
    {$group: { 
        _id: null,
        avg_delay_days: {$avg: "$rpt_delay_days"},
        median_delay_days: {$median: {
          input: "$rpt_delay_days",
          method: 'approximate'
        }},
        min_delay_days: {$min: "$rpt_delay_days"},
        max_delay_days: {$max: "$rpt_delay_days"}
    }}
])

// La mediana de los días retrasos de la denuncia por delito principal cometido.
db.crimes_modificado.aggregate([
    {$addFields: {
        rpt_delay_days: {$divide: [{$subtract: ["$date_reported", "$date_occ"]}, 86400000]}
    }},
    {$group: { 
        _id: {
            delito_principal: "$crm_cd_desc"
        },
        count: {$sum: 1},
        avg_delay_days: {$avg: "$rpt_delay_days"},
        median_delay_days: {$median: {
          input: "$rpt_delay_days",
          method: 'approximate'
        }},
        min_delay_days: {$min: "$rpt_delay_days"},
        max_delay_days: {$max: "$rpt_delay_days"}
    }},
    {$match: {count: {$gte: 100}}},
    {$sort: {median_delay_days: -1}},
    {$limit: 10}
])

/******************* Dimension Geográfica ************************/
// Conteo por Divisiones Policiales de la ciudad.
db.crimes_modificado.aggregate([
    {$group: { 
        _id: "$area_name",
        count: {$sum: 1}
    }},
    {$project: {
        _id: true,
        count: true,
        percent: {$multiply:[{$divide: ["$count", 826312]}, 100]}
    }},    
    {$sort: {percent: -1}}
])

// Incidencias de delitos en Central: 8,352.
db.crimes_modificado.find({MOcodes: {$all:["1218", "2004"]}}).count()

// Incidencias de delitos en Central: 55,862.
db.crimes_modificado.find({area_name: "Central"}).count()

// Conteo de delitos entre gente sin techo.
db.crimes_modificado.aggregate([
    {$match: {MOcodes: {$all:["1218", "2004"]}}},
    {$group: { 
        _id: "$area_name",
        count: {$sum: 1}
    }},
    {$project: {
        _id: true,
        count: true,
        percent: {$multiply:[{$divide: ["$count", 8352]}, 100]}
    }}, 
    {$sort: {count: -1}}
])

// Conteo de delitos por lugares concretos de incidencia.
db.crimes_modificado.aggregate([
    {$group: { 
        _id: "$premis_desc",
        count: {$sum: 1}
    }},
    {$project: {
        _id: true,
        count: true,
        percent: {$multiply:[{$divide: ["$count", 826312]}, 100]}
    }},    
    {$sort: {percent: -1}},
    {$limit: 10}
])

/******************* Tipología de Crimen *************************/
// Por tipología I y II.
db.crimes_modificado.aggregate([
    {$group: { 
        _id: "$part_1_2",
        count: {$sum: 1}
    }},
    {$project: {
        _id: true,
        count: true,
        percent: {$multiply:[{$divide: ["$count", 826312]}, 100]}
    }},    
    {$sort: {percent: -1}}
])

// Conteo delitos principales Part I
db.crimes_modificado.aggregate([
    {$match: {part_1_2: "1"}},
    {$group: { 
        _id: "$crm_cd_desc",
        count: {$sum: 1}
    }},
    {$sort: {count: -1}},
    {$limit: 10}
])

// Conteo delitos principales Part 2
db.crimes_modificado.aggregate([
    {$match: {part_1_2: "2"}},
    {$group: { 
        _id: "$crm_cd_desc",
        count: {$sum: 1}
    }},
    {$sort: {count: -1}},
    {$limit: 10}
])

// Por Modus Operandi.
db.crimes_modificado.aggregate([
    {$unwind: "$MOcodes"},
    {$group: { 
        _id: "$MOcodes",
        count: {$sum: 1}
    }},
    {$project: {
        _id: true,
        count: true,
        percent: {$multiply:[{$divide: ["$count", 826312]}, 100]}
    }},    
    {$sort: {percent: -1}},
    {$limit: 10}
])

/******************* Perfil de Víctimas **************************/
// Edad media de las víctimas.
db.crimes_modificado.aggregate([
    {$group: { 
        _id: null,
        avg_age: {$avg: "$victim.age"},
        median_age: {$median: {
          input: "$victim.age",
          method: 'approximate'
        }},
        min_age: {$min: "$victim.age"},
        max_age: {$max: "$victim.age"}
    }}
])

// Por sexo.
db.crimes_modificado.aggregate([
    {$group: { 
        _id: "$victim.sex",
        count: {$sum: 1}
    }},
    {$project: {
        _id: true,
        count: true,
        percent: {$multiply:[{$divide: ["$count", 826312]}, 100]}
    }},    
    {$sort: {percent: -1}}
])

// Por grupo étnico.
db.crimes_modificado.aggregate([
    {$group: { 
        _id: "$victim.descent",
        count: {$sum: 1}
    }},
    {$project: {
        _id: true,
        count: true,
        percent: {$multiply:[{$divide: ["$count", 826312]}, 100]}
    }},    
    {$sort: {percent: -1}},
    {$limit: 10}
])