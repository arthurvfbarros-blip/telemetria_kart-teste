# idade = []
# altura = []
# contador = 1

# while contador <=6:
#     try: 
#         idade_alu = int(input("Digite a idade do aluno: "))
#         altura_alu = float(input("Digite a altura do aluno: "))
#         idade.append(idade_alu)
#         altura.append(altura_alu)
#         contador += 1
#     except ValueError:
#         print("Valor inválido. Por favor, digite um número inteiro.")
#         continue

# media_altura = sum(altura)/len(altura)
# alunos_mais_velhos_e_baixos = 0

# for i in range(len(idade)):
#     if idade[i] > 13 and altura[i] < media_altura:
#         alunos_mais_velhos_e_baixos += 1

# print(f'a quantidade de alunos com mais de 13 anos e altura inferior a média é de: {alunos_mais_velhos_e_baixos}')

temperatura = []
meses = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
meses_index = []
contador = 1

while contador <=12:
    try:
        temp_mes = float(input(f'Digite a temperatua média do mês de {meses[contador-1]}: '))
        temperatura.append(temp_mes)
        contador +=1
    except ValueError:
        print("Valor inválido. Por favor, digite um número.")
        continue
media_temp = sum(temperatura)/len(temperatura)
temperaturas_acima_da_media = []

for i in range(len(temperatura)):
    if temperatura[i] > media_temp:
        temperaturas_acima_da_media.append(meses[i])
        meses_index.append(i)

print(f'Os meses com a temperatura mais quente, acima da média, foram: ')


for o in range(len(temperaturas_acima_da_media)):
    print(meses_index[o]+1, '-', temperaturas_acima_da_media[o])
