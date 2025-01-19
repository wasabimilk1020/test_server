import random
time_list=[]
minutes=str(random.randint(10, 50))
hours=["09","10","14","18","22"]
# hours=["13","15","16","23"] #파괴, 크루마, 안타, 격섬
for hour in hours:
  time_list.append(f"{hour}:{minutes}")

for i in range(hours):
    print(i)
