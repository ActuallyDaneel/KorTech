import discord
import asyncio
from asyncio import Lock
import sans
from sans.api import Api
from sans.errors import HTTPException, NotFound
from sans.utils import pretty_string
from redbot.core import checks, commands
from redbot.core.utils.chat_formatting import pagify, escape, box
from lxml import etree as ET

class Report(commands.Cog):

    def __init__(self, bot):
        Api.loop = bot.loop
        self.bot = bot
        self.delim = ', '

    @commands.command()
    async def startreport(self, ctx, user : discord.User=None):
        #Mission Summary
        await ctx.send("Mission Summary?")
        summary = ""

        while True:
            try:
                message = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author, timeout=30.0)

                summary = message.content
                break
            except asyncio.TimeoutError:
                return await ctx.send("You took too long to reply.")
            except:
                await ctx.send("Stop breaking things, try again")

        #RaidLead
        await ctx.send("Is the Raid Lead currently in the WA?")
        raidlead = ""
        rleadcount = 0
        raidmembers = ""

        while True:
            try:
                message = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author, timeout=30.0)

                if "no" in message.content.lower():
                    await ctx.send("Who was the Raid Lead?")
                    message = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author, timeout=30.0)
                    raidlead = message.content
                    break
                elif "yes" in message.content.lower():
                    try:
                        await ctx.send("Who was the Raid Lead?")
                        message = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author, timeout=30.0)

                        answer = message.content
                        raidlead = answer
                        raidwa = await self._checkwa(wanation=answer)
                        if "non-member" not in raidwa.lower():
                            raidmembers = await self._ne(wanation=answer)
                            rleadcount = await self._nec(wanation=answer)
                            break
                        else:
                            await ctx.send("Please make sure the nation is spelled correctly and is currently in the WA")

                    except NotFound:
                        await ctx.send("Nation does not exist, try again")
                    except asyncio.TimeoutError:
                        return await ctx.send("You took too long to reply.")
                else:
                    await ctx.send("Please answer yes or no")
            except asyncio.TimeoutError:
                return await ctx.send("You took too long to reply.")
        

        #DefenderLead
        await ctx.send("Who was the Defender lead?")
        defenderlead = ""
        dleadcount = 0
        defendermembers = ""

        while True:
            try:
                message = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author, timeout=30.0)

                answer = message.content
                defenderlead = answer
                defendwa = await self._checkwa(wanation=answer)
                if "non-member" not in defendwa.lower():
                    defendermembers = await self._ne(wanation=answer)
                    dleadcount = await self._nec(wanation=answer)
                    break
                else:
                    await ctx.send("Please make sure the nation is spelled correctly and is currently in the WA")

            except NotFound:
                await ctx.send("Nation does not exist, try again")
            except asyncio.TimeoutError:
                return await ctx.send("You took too long to reply.")

        #TITO Nations Count
        await ctx.send("How many TITO Members were involved?")
        membercount = 0

        while True:
            try:
                message = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author, timeout=30.0)

                membercount = float(message.content)
                break
            except ValueError:
                await ctx.send("Please enter a number")

        #TITO Nations
        await ctx.send("Which TITO Members were involved?")

        while True:
            try:
                message = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author, timeout=60.0)

                members = message.content
                break
            except asyncio.TimeoutError:
                return await ctx.send("You took too long to reply.")
            except:
                await ctx.send("How did you mess that up? Try again")

        #Coast Watching Eagle
        await ctx.send("Did anybody earn a Coast Watching Eagle?")

        while True:
            try:
                message = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author, timeout=30.0)

                if "no" in message.content.lower():
                    cwe = "No CWE"
                    break
                elif "yes" in message.content.lower():
                    await ctx.send("Who earned the CWE?")
                    message = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author, timeout=30.0)
                    cwe = message.content
                    break
                else:
                    await ctx.send("Please answer yes or no")

            except asyncio.TimeoutError:
                return await ctx.send("You took too long to reply.")
            except:
                await ctx.send("Idk how you messed that up, try again")

        #Finalization
        await ctx.send("Mission Finalized?")

        while True:
            try:
                message = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author, timeout=30.0)

                if "yes" in message.content.lower():
                    final = "Final"
                    break
                elif "no" in message.content.lower():
                    final = ""
                    break
                else:
                    await ctx.send("Please answer yes or no")
            except asyncio.TimeoutError:
                return await ctx.send("You took too long to reply.")
            except:
                await ctx.send("Stop breaking the command, try again")

        finalmsg = """{}

INVADER lead: [font color="#e61919"]{}[/font]
Endorsements Received: {} -- {}

DEFENDER lead: [font color="#00ff00"]{}[/font]
Endorsements Received: {} -- {}

[hr]TITO nations involved: {}
[font color="#ff9900"]{}[/font]

[font color="#ffff00"]{}[/font]

[font color="aqua"]{}[/font]""".format(summary, raidlead, int(float(rleadcount)), raidmembers, defenderlead, int(float(dleadcount)), defendermembers, int(membercount), members, cwe, final)

        try:
            for page in pagify(finalmsg):
                await ctx.send(page)
        except:
            await ctx.send("An error occured, please try again")

    async def _ne(self, wanation):
        """Nations Endorsing the specified WA nation"""
        Api.agent = "Kortexia"
        request = Api(
            "endorsements",
            nation=wanation,
        )
        root = await request
        pretty = pretty_string(root)
        x = pretty.partition("<ENDORSEMENTS>")
        y = ''.join(x[2]) 
        z = y.rpartition("</ENDORSEMENTS>")
        end = ''.join(z[0])
        return end

    async def _nec(self, wanation):
        """Number of Nations Endorsing (Count) the specified WA nation"""
        Api.agent = "Kortexia"
        request = Api(
            "census",
            nation=wanation,
            mode="score",
            scale="66",
        )
        root = await request
        pretty = pretty_string(root)
        x = pretty.partition("<SCORE>")
        y = ''.join(x[2]) 
        z = y.rpartition("</SCORE>")
        end = ''.join(z[0])
        return end

    async def _checkwa(self, wanation):
        """Check if Nation is in the WA"""
        Api.agent = "Kortexia"
        request = Api(
            "wa",
            nation=wanation,
        )
        root = await request
        pretty = pretty_string(root)
        return pretty