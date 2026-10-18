// teste aual
table "teste aula" {
  auth = false

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }
  
    text teste_1? filters=trim
    text teste_2? filters=trim
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
  ]

  guid = "0aDNPVdlrm_iZTXXlJv4Ecnt-sE"
}