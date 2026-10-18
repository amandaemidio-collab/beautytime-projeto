// Delete Teste record.
query "teste/{teste_id}" verb=DELETE {
  api_group = "Event Logs"

  input {
    int teste_id? filters=min:1
  }

  stack {
    db.del Teste {
      field_name = "id"
      field_value = $input.teste_id
    }
  }

  response = null
  guid = "vF1sV9c-Q2ZmqxJMksNWd9n6qcM"
}