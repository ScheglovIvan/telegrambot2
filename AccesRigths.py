# AccessRigths = {
#     "departamentsId": {
#         "ID": {
#             "stages": [1, 2, 3, 4, 5], # Номер департамента
#             "warehouse": False, # Права доступа к складу True or False
#         }
#     }
# }

AccesRigths = {
    "departamentsId": {
        "23": {   # Швеи
            "stages": ["C25:NEW", "C25:UC_XOFVER", "C25:UC_CVAEX2", "C25:UC_19LWTE"], # Номер департамента
            "warehouse": False, # Права доступа к складу True or False
        },
        "25": { # Разнорабочии
            "stages": ["C25:NEW", "C25:UC_XOFVER", "C25:UC_7AWECI", "C25:UC_JK22PF", "C25:UC_W64HWN"], # Номер департамента
            "warehouse": True, # Права доступа к складу True or False
        }
    }
}