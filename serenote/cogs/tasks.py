from discord.ext import commands

from serenote import utils, db


class Tasks(commands.Cog):
    """Commands to managing tasks."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(invoke_without_command=True)
    async def task(self, ctx, *, task):
        """Create a new task.

        ```
        +task <name>
        <details>
        ```
        """
        await ctx.message.delete()
        lines = task.split("\n")
        if len(lines) == 1:
            await utils.Task.create_task(ctx.channel, ctx.author.id, lines[0])
        else:
            await utils.Task.create_task(ctx.channel, ctx.author.id, lines[0], "\n".join(lines[1:]))

    @commands.Cog.listener(name='on_raw_reaction_add')
    async def task_action_add(self, payload):
        """Run task.action if the added reaction is on the task message."""
        if task := self.get_task(self, payload):
            await task.action(payload, True)

    @commands.Cog.listener(name='on_raw_reaction_remove')
    async def task_action_remove(self, payload):
        """Run task.action if the removed reaction is on the task message."""
        if task := self.get_task(self, payload):
            await task.action(payload, False)
    
    @commands.Cog.listener(name='on_message_delete')
    async def task_delete(self, message):
        """Run task delete if the user deletes the deleted."""
        if task_obj := db.get_task(message.id):
            task_obj.delete()
    
    async def get_task(self, payload):
        """Return task object from reaction payload."""
        if not (task_obj := db.get_task(payload.message_id)):
            return

        task_msg = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
        return utils.Task(task_msg, task_obj)


def setup(bot):
    bot.add_cog(Tasks(bot))
