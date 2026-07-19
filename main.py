from src.tracker import Tracker,TrackerSearh

def get_topics():
    topics = []
    while True:
        topic = input("Enter a topic (or /q to stop): ")
        if topic == "/q":
            break
        if topic:
            topics.append(topic)
    return topics

if __name__ == "__main__":
    # t = Tracker()
    # menu_q = 0
    # while menu_q != 5:

    #     menu_q = int(input(
    #         "Enter \n1 to add problem\n2 to update problem\n3 to delete problem\n4 to view all problems\n5 to exit\n"
    #     ))

    #     if menu_q == 1:
    #         print(t.add_problems(
    #             id=int(input("Enter id: ")),
    #             title=input("Enter title: "),
    #             difficulty=input("Enter difficulty: "),
    #             topics=get_topics()
    #         ))

    #     elif menu_q == 2:
    #         t.update_problem(
    #             id=int(input("Enter id: ")),
    #             title=input("Enter title: "),
    #             difficulty=input("Enter difficulty: "),
    #             topics=get_topics()
    #         )
    #     elif menu_q == 3:
    #         t.delete_problem(
    #             id=int(input("Enter id: "))
    #         )

    #     elif menu_q == 4:
    #         if t.problems:
    #             for p in t.problems:
    #                 print(p)
    #         else:
    #             print("No problems found.")

    t = TrackerSearh()
    # print(t.search_by_topic("array"))
    # print(t.search_by_difficulty("easy"))
    # print(t.search_by_id(1))
    print(t.search("2"))
    print(t.search("array"))
    print(t.search("easy"))
    print("Thank you!")