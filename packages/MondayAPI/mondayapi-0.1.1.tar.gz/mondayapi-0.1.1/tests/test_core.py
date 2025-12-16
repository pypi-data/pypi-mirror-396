from src.MondayAPI.Query import Query

q = Query()
q.boards.id.activate()
q.boards.items_page.items.name.activate()
q.boards.items_page.items.id.activate()
q.boards.items_page.cursor.activate()
q.boards.arguments = {'ids': [9169256232]}

data = q.execute()

q2 = Query()
q2.next_items_page.items.id.activate()
q2.next_items_page.items.name.activate()
q2.next_items_page.cursor.activate()
q2.next_items_page.arguments = {'cursor': f'"{data.data.boards[0].items_page.cursor}"'}

b = q2.execute()
pass