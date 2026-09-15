from search import search_prompt

def main():

    user_question = input("PERGUNTA: ")
    if not user_question:
        print("Usuário não forneceu uma pergunta. Encerrando o programa.")
        return
    
    chain = search_prompt(user_question)

    if not chain:
        print("Não foi possível iniciar o chat. Verifique os erros de inicialização.")
        return
    
    print("RESPOSTA:", chain)
    
    pass

if __name__ == "__main__":
    main()