// Edit Teste record
query "teste/{teste_id}" verb=PATCH {
  api_group = "Event Logs"

  input {
    int teste_id? filters=min:1
    dblink {
      table = "Teste"
    }
  }

  stack {
    util.get_raw_input {
      encoding = "json"
      exclude_middleware = false
    } as $raw_input
  
    db.patch Teste {
      field_name = "id"
      field_value = $input.teste_id
      data = `$input|pick:($raw_input|keys)`|filter_null|filter_empty_text
    } as $teste
  }

  response = $teste
  guid = "25vdmqwjcnsmZTVxGg6jlTu3vIk"
}