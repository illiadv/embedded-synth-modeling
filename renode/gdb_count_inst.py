import gdb

class CountInstructions(gdb.Command):
  """Steps through the current function and counts machine instructions."""
  def __init__(self):
      super(CountInstructions, self).__init__("count_inst", gdb.COMMAND_USER)

  def invoke(self, arg, from_tty):
      gdb.execute("set python print-stack full", to_string=True)
      start_frame = gdb.newest_frame()
      caller_frame = gdb.newest_frame().older()
      count = 0
      
      while True:
          gdb.execute("stepi", to_string=True)
          count += 1
          
          try:
              current_frame = gdb.newest_frame()
          except gdb.error as e:
              break

          if current_frame == caller_frame:
              break
              
      print(f"Instructions executed: {count}")

CountInstructions()
