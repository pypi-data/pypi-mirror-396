from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()

LOGO = Align.center(
	Panel.fit(
		Text(
			"""
      .__    .___                                                          
___  _|__| __| _/____  ____             ____________   ____   ____   ______
\  \/ /  |/ __ |/ __ \/  _ \   ______  /  ___/\____ \_/ __ \_/ ___\ /  ___/
 \   /|  / /_/ \  ___(  <_> ) /_____/  \___ \ |  |_> >  ___/\  \___ \___ \ 
  \_/ |__\____ |\___  >____/          /____  >|   __/ \___  >\___  >____  >
              \/    \/                     \/ |__|        \/     \/     \/ 
            """,
			style="blue_violet"
		),
		border_style="yellow3",
		padding=(1, 6)
	)
)
