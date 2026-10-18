// Query all Unicidade records
query unicidade verb=GET {
  api_group = "aula unicidade"

  input {
  }

  stack {
    db.query Unicidade {
      return = {type: "list"}
    } as $unicidade
  }

  response = $unicidade
  guid = "nwQVBjn--mjH7JnKvQQRx5Sa02E"
}