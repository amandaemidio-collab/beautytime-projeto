table Unicidade {
  auth = false

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }
  
    text CPF? filters=trim|min:12
    text RA? filters=trim
    int status_cpf_id? {
      table = "STATUS_CPF"
    }
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
    {type: "btree|unique", field: [{name: "CPF", op: "asc"}]}
    {type: "btree|unique", field: [{name: "RA", op: "asc"}]}
    {type: "btree", field: [{name: "CPF", op: "asc"}]}
  ]

  guid = "2bSXnmUSuvYYyuZjeTkjhAobz3E"
}