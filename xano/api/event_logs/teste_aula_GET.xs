// Query all teste aula records
query teste_aula verb=GET {
  api_group = "Event Logs"

  input {
  }

  stack {
    db.query "teste aula" {
      return = {type: "list"}
    } as $teste_aula
  }

  response = $teste_aula
  guid = "3nwuCqdxkhphg5f8GFw9c_LnOZw"
}