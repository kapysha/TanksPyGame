from sqlalchemy import update, select
from database.config import session, Main
import threading


def add_shots(owner: str) -> None:
    def increment_shot():
        if owner == 'ai':
            field = Main.ai_total_shots
        else:
            field = Main.player_total_shots

        with session() as sess:
            sess.execute(update(Main).values({field: field + 1}))
            sess.commit()

    threading.Thread(target=increment_shot, daemon=True).start()


def get_info() -> tuple:
    with session() as sess:
        result = sess.execute(select(*[col for col in Main.__table__.columns if col != Main.id]))
        return result.first()


def update_battle_stats(winner: str, battle_duration: float):
    with session() as sess:
        battle_duration = round(battle_duration, 2)
        stats = sess.execute(select(Main)).scalar_one_or_none()
        if stats:
            current_longest = stats.longest_battle_duration or 0
            current_shortest = stats.shortest_battle_duration or float('inf')

            sess.execute(
                update(Main).values({
                    Main.total_battles: Main.total_battles + 1,
                    Main.longest_battle_duration: max(current_longest, battle_duration),
                    Main.shortest_battle_duration: min(current_shortest, battle_duration),
                    Main.player_wins: Main.player_wins + (1 if winner == 'player' else 0),
                    Main.ai_wins: Main.ai_wins + (1 if winner == 'ai' else 0)
                })
            )
            sess.commit()
