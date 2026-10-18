// teste aula
table Teste {
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

  guid = "nYkY3sfpsgXTXMPvJMb5RM1w480"
}