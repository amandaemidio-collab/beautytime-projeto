// Get Teste record
query "teste/{teste_id}" verb=GET {
  api_group = "Event Logs"

  input {
    int teste_id? filters=min:1
  }

  stack {
    db.get Teste {
      field_name = "id"
      field_value = $input.teste_id
    } as $teste
  
    precondition ($teste != null) {
      error_type = "notfound"
      error = "Not Found."
    }
  }

  response = $teste
  guid = "FKQuWQSPtHzucI8tpM_TSOMZapc"
}