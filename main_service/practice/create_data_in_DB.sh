LOG_FILE="./practice/create_data_in_DB.log"

if [ ! -f "$LOG_FILE" ]
then
# Создание клиентов
    echo "Creating data in DB" | tee -a "$LOG_FILE"
    curl -X POST -H "Content-Type: application/json" -d '{"client_name": "Иванов Иван Иванович", "comment": "Первый клиент службы такси"}' http://main:8000/mainservice_api/v1/clients/ | tee -a "$LOG_FILE"
    curl -X POST -H "Content-Type: application/json" -d '{"client_name": "Казенин Юрий Васильевич", "comment": "Второй клиент службы такси"}' http://main:8000/mainservice_api/v1/clients/ | tee -a "$LOG_FILE"
    curl -X POST -H "Content-Type: application/json" -d '{"client_name": "Петров Петр Петрович", "comment": ""}' http://main:8000/mainservice_api/v1/clients/ | tee -a "$LOG_FILE"
    curl -X POST -H "Content-Type: application/json" -d '{"client_name": "Сидоров Николай Петрович", "comment": ""}' http://main:8000/mainservice_api/v1/clients/ | tee -a "$LOG_FILE"
    curl -X POST -H "Content-Type: application/json" -d '{"client_name": "Смирнова Марина Олеговна", "comment": ""}' http://main:8000/mainservice_api/v1/clients/ | tee -a "$LOG_FILE"

# Создание автомобилей
    curl -X POST -H "Content-Type: application/json" -d '{"model": "Lada GRANTA", "color":"blue", "production_date":"2018-12-23", "vin_number":"XTA210930Y2696785", "reg_number": "A123AA43", "comment": "Первый автомобиль службы такси"}' http://main:8000/mainservice_api/v1/cars/ | tee -a "$LOG_FILE"
    curl -X POST -H "Content-Type: application/json" -d '{"model": "Lada VESTA", "color":"white", "production_date":"2018-12-24", "vin_number":"XTA210930Y1234567", "reg_number": "B321BB43", "comment": ""}' http://main:8000/mainservice_api/v1/cars/ | tee -a "$LOG_FILE"
    curl -X POST -H "Content-Type: application/json" -d '{"model": "Lada VESTA", "color":"green", "production_date":"2018-12-25", "vin_number":"XTA210930Y2345678", "reg_number": "C111CC43", "comment": ""}' http://main:8000/mainservice_api/v1/cars/ | tee -a "$LOG_FILE"
    curl -X POST -H "Content-Type: application/json" -d '{"model": "Lada VESTA", "color":"green", "production_date":"2018-12-26", "vin_number":"XTA210930Y3456789", "reg_number": "C222CC43", "comment": ""}' http://main:8000/mainservice_api/v1/cars/ | tee -a "$LOG_FILE"
    curl -X POST -H "Content-Type: application/json" -d '{"model": "Lada VESTA", "color":"green", "production_date":"2018-12-27", "vin_number":"XTA210930Y4567890", "reg_number": "C333CC43", "comment": ""}' http://main:8000/mainservice_api/v1/cars/ | tee -a "$LOG_FILE"

# Создание водителей
    curl -X POST -H "Content-Type: application/json" -d '{"driver_name":"Борисов Борис Борисович", "driver_license":"АА123456", "comment":"Первый водитель сервиса такси"}' http://main:8000/mainservice_api/v1/drivers/ | tee -a "$LOG_FILE"
    curl -X POST -H "Content-Type: application/json" -d '{"driver_name":"Романов Роман Романович", "driver_license":"АА234567", "comment":""}' http://main:8000/mainservice_api/v1/drivers/ | tee -a "$LOG_FILE"
    curl -X POST -H "Content-Type: application/json" -d '{"driver_name":"Константинов Константин Константинович", "driver_license":"АА345678", "comment":""}' http://main:8000/mainservice_api/v1/drivers/ | tee -a "$LOG_FILE"
    curl -X POST -H "Content-Type: application/json" -d '{"driver_name":"Александров Александр Александрович", "driver_license":"АА456789", "comment":""}' http://main:8000/mainservice_api/v1/drivers/ | tee -a "$LOG_FILE"
    curl -X POST -H "Content-Type: application/json" -d '{"driver_name":"Сидоров Сидор Сидорович", "driver_license":"АА567890", "comment":""}' http://main:8000/mainservice_api/v1/drivers/ | tee -a "$LOG_FILE"
    curl -X POST -H "Content-Type: application/json" -d '{"driver_name":"Алексеев Алексей Алексеевич", "driver_license":"АА678901", "comment":""}' http://main:8000/mainservice_api/v1/drivers/ | tee -a "$LOG_FILE"
    curl -X POST -H "Content-Type: application/json" -d '{"driver_name":"Антонов Антон Антонович", "driver_license":"АА789012", "comment":""}' http://main:8000/mainservice_api/v1/drivers/ | tee -a "$LOG_FILE"
    
fi
