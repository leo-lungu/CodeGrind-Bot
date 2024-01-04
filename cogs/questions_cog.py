import os
import random
import discord
from discord.ext import commands
from bot_globals import logger
from embeds.questions_embeds import (daily_question_embed, random_question_embed, search_question_embed)
from middleware import track_analytics, defer_interaction, ensure_server_document

class Questions(commands.GroupCog, name="question"):
    def __init__(self, client: commands.Bot):
        self.client = client

    @discord.app_commands.command(name="search", description="Search for a LeetCode question")
    @defer_interaction()
    @track_analytics
    async def search_question(self, interaction: discord.Interaction, name_id_or_url: str) -> None:
        logger.info("file: cogs/questions.py ~ display_question ~ run")
        embed = await search_question_embed(name_id_or_url)
        await interaction.followup.send(embed=embed)

    @discord.app_commands.command(name="daily", description="Get the daily question")
    @defer_interaction()
    @track_analytics
    async def daily_question(self, interaction: discord.Interaction) -> None:
        logger.info("file: cogs/questions.py ~ get_daily ~ run")
        embed = await daily_question_embed()
        await interaction.followup.send(embed=embed)

    @discord.app_commands.command(name="random", description="Get a random question of your desired difficulty")
    @defer_interaction()
    @track_analytics
    async def random_question(self, interaction: discord.Interaction, difficulty: str = "random") -> None:
        logger.info("file: cogs/questions.py ~ question ~ run ~ difficulty: %s", difficulty)
        difficulty = difficulty.lower()
        embed = await random_question_embed(difficulty)
        await interaction.followup.send(embed=embed)

    async def get_random_question(self, company_name: str):
        # Constructing an absolute path to the file
        dir_path = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(dir_path, 'companies', f'{company_name}.txt')

        # Check if the file exists
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return None, "Company file not found."

        try:
            with open(file_path, 'r') as file:
                questions = file.readlines()
                if questions:
                    return random.choice(questions).strip(), None
                else:
                    return None, "No questions found for this company."
        except Exception as e:
            logger.error(f"Error reading file: {e}")
            return None, "An error occurred while reading the file."

    @discord.app_commands.command(name="company", description="Return a random question for the given company from previous interviews")
    @defer_interaction(user_preferences_prompt=True)
    @ensure_server_document
    @track_analytics
    async def company(self, interaction: discord.Interaction, company_name: str) -> None:
        logger.info("file: cogs/companies.py ~ company ~ run")

        question_identifier, error_message = await self.get_random_question(company_name)

        if error_message:
            await interaction.followup.send(error_message)
            return

        embed = await search_question_embed(question_identifier)
        await interaction.followup.send(embed=embed)

async def setup(client: commands.Bot) -> None:
    await client.add_cog(Questions(client))
