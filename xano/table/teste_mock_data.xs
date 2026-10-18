table TESTE_MOCK_DATA {
  auth = false

  schema {
    int id
    text first_name?
    text last_name?
    email email?
    text gender?
    text ip_address?
  }

  index = [{type: "primary", field: [{name: "id"}]}]
  guid = "yeY20DFJYqcTOwGeBKPGTg9XbdA"
}