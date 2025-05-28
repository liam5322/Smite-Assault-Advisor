#!/usr/bin/env python3
"""
🤖 SMITE 2 Assault Brain Discord Bot
Easy setup for your Discord server!

Setup:
1. pip install discord.py
2. Create bot at https://discord.com/developers/applications
3. Add bot token below
4. Invite bot to your server
5. Run: python discord_bot.py
"""

import discord
from discord.ext import commands
import requests
import json
import asyncio
from datetime import datetime

# ⚠️ ADD YOUR BOT TOKEN HERE
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
ASSAULT_BRAIN_URL = "http://localhost:9000"

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

class AssaultBrainBot:
    def __init__(self):
        self.server_url = ASSAULT_BRAIN_URL
    
    async def analyze_teams(self, team1, team2):
        """Analyze teams via Assault Brain API"""
        try:
            response = requests.post(
                f"{self.server_url}/api/analyze",
                json={"team1": team1, "team2": team2},
                timeout=10
            )
            return response.json()
        except Exception as e:
            return {"error": f"Analysis failed: {e}"}
    
    def create_analysis_embed(self, result, team1, team2):
        """Create Discord embed for analysis"""
        if "error" in result:
            embed = discord.Embed(
                title="❌ Analysis Error",
                description=result["error"],
                color=0xff4444
            )
            if "valid_gods" in result:
                embed.add_field(
                    name="✅ Valid SMITE 2 Gods (Examples)",
                    value=", ".join(result["valid_gods"][:8]),
                    inline=False
                )
            return embed
        
        # Success analysis
        win_rate = f"{result['win_probability']:.1%}"
        confidence = result.get('confidence', 'medium').title()
        
        embed = discord.Embed(
            title="🎮 SMITE 2 Assault Analysis",
            description=f"**Win Rate: {win_rate}** ({confidence} Confidence)",
            color=0x00ff88
        )
        
        # Teams
        embed.add_field(
            name="👥 Your Team",
            value=" • ".join(team1),
            inline=False
        )
        embed.add_field(
            name="👥 Enemy Team", 
            value=" • ".join(team2),
            inline=False
        )
        
        # Priority items
        if result.get('item_priorities'):
            embed.add_field(
                name="🔥 Priority Items (Assault Meta)",
                value="\n".join(result['item_priorities'][:4]),
                inline=False
            )
        
        # Strategic advice
        if result.get('key_advice'):
            embed.add_field(
                name="⚡ Strategic Advice",
                value="\n".join(result['key_advice'][:3]),
                inline=False
            )
        
        # Footer with stats
        analysis_time = result.get('analysis_time_ms', 0)
        embed.set_footer(text=f"⏱️ Analysis: {analysis_time:.1f}ms | 🎮 Mode: Assault")
        
        return embed

# Initialize brain
brain = AssaultBrainBot()

@bot.event
async def on_ready():
    print(f'🤖 {bot.user} is ready to analyze Assault!')
    print(f'📊 Connected to {len(bot.guilds)} servers')
    
    # Test connection to Assault Brain
    try:
        response = requests.get(ASSAULT_BRAIN_URL, timeout=5)
        print("✅ Assault Brain connection successful!")
    except:
        print("❌ Warning: Assault Brain server not responding")
        print("   Make sure to run: python web_demo.py")

@bot.command(name='assault')
async def assault_analyze(ctx, *, teams_input):
    """
    Analyze SMITE 2 Assault team compositions
    
    Usage:
    !assault Zeus Ares Neith Ra Ymir vs Artemis Fenrir Kukulkan Geb Janus
    !assault analyze Aphrodite Ra vs Zeus Poseidon (minimum 2v2)
    """
    try:
        # Parse teams
        if ' vs ' not in teams_input.lower():
            await ctx.send("❌ Use format: `!assault Team1 vs Team2`\nExample: `!assault Zeus Ares vs Artemis Neith`")
            return
        
        parts = teams_input.lower().split(' vs ')
        if len(parts) != 2:
            await ctx.send("❌ Use format: `!assault Team1 vs Team2`")
            return
        
        team1_str, team2_str = parts
        team1 = [god.strip().title() for god in team1_str.split() if god.strip()]
        team2 = [god.strip().title() for god in team2_str.split() if god.strip()]
        
        if len(team1) < 1 or len(team2) < 1:
            await ctx.send("❌ Each team needs at least 1 god!")
            return
        
        if len(team1) > 5 or len(team2) > 5:
            await ctx.send("❌ Maximum 5 gods per team (Assault format)!")
            return
        
        # Show typing indicator
        async with ctx.typing():
            # Analyze teams
            result = await brain.analyze_teams(team1, team2)
            
            # Create and send embed
            embed = brain.create_analysis_embed(result, team1, team2)
            await ctx.send(embed=embed)
    
    except Exception as e:
        await ctx.send(f"❌ Error: {e}")

@bot.command(name='gods')
async def list_gods(ctx):
    """List valid SMITE 2 gods"""
    try:
        # Get gods from API
        response = requests.post(
            f"{ASSAULT_BRAIN_URL}/api/analyze",
            json={"team1": ["InvalidGod"], "team2": ["AnotherInvalid"]},
            timeout=5
        )
        result = response.json()
        
        if "valid_gods" in result:
            gods = result["valid_gods"]
            total = result.get("total_gods", len(gods))
            
            embed = discord.Embed(
                title="🎮 SMITE 2 Gods Database",
                description=f"**{total} confirmed gods available**",
                color=0x00aaff
            )
            
            # Split gods into chunks for multiple fields
            chunk_size = 10
            for i in range(0, len(gods), chunk_size):
                chunk = gods[i:i+chunk_size]
                field_name = f"Gods {i+1}-{min(i+chunk_size, len(gods))}"
                embed.add_field(
                    name=field_name,
                    value=" • ".join(chunk),
                    inline=True
                )
            
            embed.set_footer(text="Use these gods in !assault commands")
            await ctx.send(embed=embed)
        else:
            await ctx.send("❌ Could not fetch gods list")
    
    except Exception as e:
        await ctx.send(f"❌ Error fetching gods: {e}")

@bot.command(name='help_assault')
async def help_assault(ctx):
    """Show Assault Brain help"""
    embed = discord.Embed(
        title="🎮 SMITE 2 Assault Brain Commands",
        description="AI-powered team analysis for Assault mode!",
        color=0x00ff88
    )
    
    embed.add_field(
        name="📊 Analysis Commands",
        value="""
        `!assault Zeus Ares vs Artemis Neith` - Quick 2v2 analysis
        `!assault Zeus Ares Neith Ra Ymir vs Artemis Fenrir Kukulkan Geb Janus` - Full 5v5
        """,
        inline=False
    )
    
    embed.add_field(
        name="📋 Other Commands",
        value="""
        `!gods` - List all valid SMITE 2 gods
        `!help_assault` - Show this help
        """,
        inline=False
    )
    
    embed.add_field(
        name="🔥 What You Get",
        value="""
        • Win probability calculation
        • Smart item recommendations (anti-heal, spectral, etc.)
        • Strategic advice for Assault meta
        • SMITE 2 god validation
        • Sub-2ms analysis speed
        """,
        inline=False
    )
    
    embed.set_footer(text="Web interface: http://localhost:9000")
    await ctx.send(embed=embed)

@bot.event
async def on_command_error(ctx, error):
    """Handle command errors"""
    if isinstance(error, commands.CommandNotFound):
        return  # Ignore unknown commands
    
    await ctx.send(f"❌ Error: {error}")

def main():
    """Run the Discord bot"""
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("❌ Please add your Discord bot token to BOT_TOKEN variable!")
        print("Get one at: https://discord.com/developers/applications")
        return
    
    print("🚀 Starting SMITE 2 Assault Brain Discord Bot...")
    print("Commands: !assault, !gods, !help_assault")
    
    try:
        bot.run(BOT_TOKEN)
    except discord.LoginFailure:
        print("❌ Invalid bot token!")
    except Exception as e:
        print(f"❌ Bot error: {e}")

if __name__ == "__main__":
    main()