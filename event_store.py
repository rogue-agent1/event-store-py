import time
class Event:
    def __init__(s, type, data, stream="default"):
        s.type=type;s.data=data;s.stream=stream;s.timestamp=time.monotonic();s.version=0
    def __repr__(s): return f"Event({s.type}, v{s.version})"
class EventStore:
    def __init__(s): s.events=[]; s.projections={}
    def append(s, event):
        event.version = len(s.events); s.events.append(event)
        for name, proj in s.projections.items(): proj["fn"](proj["state"], event)
        return event.version
    def get_stream(s, stream): return [e for e in s.events if e.stream==stream]
    def get_by_type(s, type): return [e for e in s.events if e.type==type]
    def replay(s, stream=None):
        events = s.get_stream(stream) if stream else s.events
        return list(events)
    def add_projection(s, name, initial_state, fn):
        state = dict(initial_state) if isinstance(initial_state, dict) else initial_state
        s.projections[name] = {"state": state, "fn": fn}
        for e in s.events: fn(state, e)
    def get_projection(s, name): return s.projections[name]["state"]
def demo():
    store = EventStore()
    def balance_proj(state, event):
        if event.type == "deposited": state["balance"] = state.get("balance", 0) + event.data["amount"]
        elif event.type == "withdrawn": state["balance"] = state.get("balance", 0) - event.data["amount"]
    store.add_projection("balance", {"balance": 0}, balance_proj)
    store.append(Event("deposited", {"amount": 100}, "account-1"))
    store.append(Event("deposited", {"amount": 50}, "account-1"))
    store.append(Event("withdrawn", {"amount": 30}, "account-1"))
    print(f"Balance: {store.get_projection('balance')}")
    print(f"All events: {len(store.events)}")
    print(f"Deposits: {len(store.get_by_type('deposited'))}")
if __name__ == "__main__": demo()
