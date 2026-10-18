// Get Unicidade record
query "unicidade/{unicidade_id}" verb=GET {
  api_group = "aula unicidade"

  input {
    int unicidade_id? filters=min:1
  }

  stack {
    db.get Unicidade {
      field_name = "id"
      field_value = $input.unicidade_id
    } as $unicidade
  
    precondition ($unicidade != null) {
      error_type = "notfound"
      error = "Not Found."
    }
  }

  response = $unicidade
  guid = "yljvUAfjN6lH5MfrH-VEdmc1pmw"
}