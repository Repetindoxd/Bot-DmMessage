import discord
from discord.ext import commands
import asyncio

# Configurações do bot
intents = discord.Intents.default()
intents.members = True  # Necessário para acessar membros do servidor
intents.message_content = True  # Necessário para ler mensagens

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Bot {bot.user} está online!')
    print(f'Conectado em {len(bot.guilds)} servidores')

@bot.command()
async def enviardm(ctx, *, mensagem: str = None):
    """
    Envia uma mensagem na DM de todos os membros do servidor
    Uso: !enviardm <mensagem>
    """
    
    if mensagem is None:
        await ctx.send("❌ Por favor, forneça uma mensagem. Exemplo: `!enviardm Olá a todos!`")
        return
    
    # Verifica se o autor tem permissão (opcional - pode personalizar)
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ Você precisa ser administrador para usar este comando.")
        return
    
    # Confirmação antes de enviar
    embed = discord.Embed(
        title="⚠️ Confirmar Envio de DMs",
        description=f"Você tem certeza que deseja enviar a seguinte mensagem para **{ctx.guild.member_count}** membros?",
        color=discord.Color.yellow()
    )
    embed.add_field(name="Mensagem:", value=mensagem, inline=False)
    embed.add_field(name="Tempo estimado:", value=f"Aproximadamente {ctx.guild.member_count * 2} segundos", inline=False)
    embed.set_footer(text="Digite 'sim' para confirmar ou 'cancelar' para cancelar")
    
    confirm_msg = await ctx.send(embed=embed)
    
    # Verifica a resposta
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel
    
    try:
        response = await bot.wait_for('message', timeout=30.0, check=check)
        
        if response.content.lower() == 'sim':
            await confirm_msg.delete()
            await response.delete()
            
            # Inicia o envio
            processing_msg = await ctx.send("🔄 Iniciando o envio de DMs...")
            
            success = 0
            failed = 0
            total = len(ctx.guild.members)
            
            # Loop para enviar DMs
            for member in ctx.guild.members:
                try:
                    # Evita enviar para bots
                    if member.bot:
                        continue
                    
                    # Tenta enviar a mensagem
                    dm_embed = discord.Embed(
                        title=f"Mensagem do servidor: {ctx.guild.name}",
                        description=mensagem,
                        color=discord.Color.blue()
                    )
                    dm_embed.set_footer(text=f"Enviado por: {ctx.author.display_name}")
                    
                    await member.send(embed=dm_embed)
                    success += 1
                    
                    # Atualiza o status a cada 10 envios
                    if success % 10 == 0:
                        await processing_msg.edit(content=f"🔄 Enviando... {success}/{total} DMs enviadas")
                    
                    # Delay para evitar rate limits do Discord
                    await asyncio.sleep(2)
                    
                except discord.Forbidden:
                    # Usuário bloqueou DMs ou não permite
                    failed += 1
                    continue
                except Exception as e:
                    failed += 1
                    print(f"Erro ao enviar para {member}: {e}")
                    continue
            
            # Resumo final
            summary_embed = discord.Embed(
                title="✅ Envio de DMs Concluído",
                color=discord.Color.green()
            )
            summary_embed.add_field(name="✅ Enviadas com sucesso", value=str(success), inline=True)
            summary_embed.add_field(name="❌ Falhas", value=str(failed), inline=True)
            summary_embed.add_field(name="👥 Total de membros", value=str(total), inline=True)
            summary_embed.add_field(name="📝 Mensagem enviada", value=mensagem[:500] + ("..." if len(mensagem) > 500 else ""), inline=False)
            
            await processing_msg.delete()
            await ctx.send(embed=summary_embed)
            
        elif response.content.lower() == 'cancelar':
            await confirm_msg.delete()
            await response.delete()
            await ctx.send("❌ Envio cancelado.")
        else:
            await confirm_msg.delete()
            await response.delete()
            await ctx.send("❌ Comando não reconhecido. Envio cancelado.")
            
    except asyncio.TimeoutError:
        await confirm_msg.delete()
        await ctx.send("⏰ Tempo esgotado. Envio cancelado.")

# Comando de ajuda específico
@bot.command()
async def ajuda(ctx):
    embed = discord.Embed(
        title="📚 Comandos do Bot",
        description="Lista de comandos disponíveis",
        color=discord.Color.blue()
    )
    embed.add_field(
        name="!enviardm <mensagem>",
        value="Envia uma mensagem na DM de todos os membros do servidor (apenas administradores)",
        inline=False
    )
    embed.add_field(
        name="Notas importantes:",
        value="• O bot precisa da intenção 'Membros' ativada\n• Membros podem ter DMs bloqueadas\n• Há um delay entre envios para evitar rate limits",
        inline=False
    )
    await ctx.send(embed=embed)

# Token do bot (NUNCA compartilhe isso publicamente!)
TOKEN = 'Seu token'

if __name__ == "__main__":
    bot.run(TOKEN)
