// Get teste aula record
query "teste_aula/{teste_aula_id}" verb=GET {
  api_group = "Event Logs"

  input {
    int teste_aula_id? filters=min:1
  }

  stack {
    db.get "teste aula" {
      field_name = "id"
      field_value = $input.teste_aula_id
    } as $teste_aula
  
    precondition ($teste_aula != null) {
      error_type = "notfound"
      error = "Not Found."
    }
  }

  response = $teste_aula
  guid = "hM6rZ_3jYCbofPWHaTokjRIM_cA"
}