import discord
import os

from bs4 import BeautifulSoup as bs

from the_brain import api_call

class BalderRecommendationModal(discord.ui.Modal, title="Balder WA Recommendation"):
    def __init__(self, bot, council, position, title):
        super().__init__()
        self.bot = bot
        self.council = council
        self.position = position
        self.title = title

    recommendation = discord.ui.TextInput(
        style=discord.TextStyle.long,
        label="Recommendation",
        placeholder="Recommendation goes here"
    )

    async def on_submit(self, modal_interaction: discord.Interaction):
        await modal_interaction.response.defer()

        f = open("logs/watchers.txt", "r")
        watchers = [f"[nation]{watcher}[/nation]" for watcher in f.read().split(",")]
        f.close()

        message = "[b]Greetings![/b]\n\nThe Ministry of World Assembly Affairs has issued a recommendation regarding an at-vote resolution:\n\n[b]Resolution: [url=https://www.nationstates.net/page=@@COUNCIL@@]@@TITLE@@[/url][/b]\n\n[b]Recommendation: @@POSITION@@[/b]\n\n[spoiler=Ministry Analysis]@@RECOMMENDATION@@[/spoiler]\n\nPlease let us know if you have any questions.\n[spoiler=Recommendation Notifications]@@WATCHERS@@[/spoiler]"
        formatted_message = message.replace("@@COUNCIL@@", "ga" if self.council == "1" else "sc").replace("@@TITLE@@", self.title).replace("@@POSITION@@", self.position).replace("@@RECOMMENDATION@@", self.recommendation.value).replace("@@WATCHERS@@", ", ".join(watchers[:-1]) + ', and ' + watchers[-1] if len(watchers) > 1 else watchers[0])

        data = {
            'nation': os.getenv("BALDER_WA_NATION"),
            'region': os.getenv("BALDER_WA_REGION"),
            'c': 'rmbpost',
            'text': formatted_message,
            'mode': 'prepare'
        }

        prep_request = api_call(url="https://www.nationstates.net/cgi-bin/api.cgi", mode=3, data=data, pin=os.getenv("Balder-WA-X-Pin"))

        print(os.environ["BALDER-WA-X-Pin"])
        os.environ["BALDER-WA-X-Pin"] = prep_request.headers.get("X-Pin") if prep_request.headers.get("X-Pin") else os.environ["BALDER-WA-X-Pin"]
        data['token'] = bs(prep_request.text, "xml").find_all("SUCCESS")
        data['mode'] = "execute"

        execute_request = api_call(url="https://www.nationstates.net/cgi-bin/api.cgi", mode=3, data=data, pin=os.getenv("BALDER-WA-X-Pin"))

        await modal_interaction.followup.send("Recommendation Posted!")

    async def on_error(self, modal_interaction: discord.Interaction, error: Exception) -> None:
        await modal_interaction.followup.send(error, ephemeral=True)

    async def on_timeout(self) -> None:
        for child in self.children:
            child.disabled = True

        await self.response.edit(view=self)