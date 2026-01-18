import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import View, Button, Select, Modal, TextInput
from datetime import datetime

# ==========================================
# --- КОНФИГУРАЦИЯ (ВСТАВЬ СВОИ ID) ---
# ==========================================
TOKEN = 'MTQ2MjM2OTk0ODkzNTUyMDM2Mw.Gat8qX.3t2uxwjx0aYMWv3fD7NhRjWsOECYMwJ3YkJkbw'
GUILD_ID = 1228340209540665375         # Твой сервер
OWNER_ID = 1147184359581946006         # Ты
ROLE_ADMIN_ID = 1321779775970345000    # Высшая админка
LOG_CHANNEL_ID = 1321780543385501738   # Канал, где админы видят все действия бота

# Гендерные роли
ROLE_BOY = 1462375254369501336
ROLE_GIRL = 1462375094033846364

# Категории
CAT_EVENTS_ID = 1321780071169785899
CAT_CLOSES_ID = 1321780079994343505

# Настройка персонала и логов анкет
STAFF_CONFIG = {
    "Модератор": {"role": 101, "curator": 201, "log": 301},
    "Ивентер":   {"role": 102, "curator": 202, "log": 302},
    "Креатив":   {"role": 103, "curator": 203, "log": 303},
    "Саппорт":   {"role": 104, "curator": 204, "log": 304},
    "Клозер":    {"role": 105, "curator": 205, "log": 305},
    "Ведущий":   {"role": 106, "curator": 206, "log": 306},
}

# Списки игр
GAMES_DATA = {
    "MEME-POLICE": ["Brainwave", "Декодер", "Имаджинариум", "Криминалист", "Коднеймс", "Намек понял", "Психушка", "Секретный гитлер", "Слова-мины", "Цитадели", "Шляпа", "Шпион"],
    "BOARD GAMES": ["Бабочки", "Гномы вредители", "Грани судьбы", "Колоретто", "Корова", "Кости", "Кубички", "Овечки", "Селестия", "Соло", "Стелла", "Счастливые числа", "Сыщики", "Ток", "Токайдо"],
    "ПРОЧЕЕ": ["Among us", "Anime music quiz", "Brawlhalla", "Dead by daylight", "Goose goose duck", "Hearthstone", "Jackbox", "Make it meme", "Minecraft", "Phasmophobia", "Raft", "Roblox", "Stardew valley", "Terraria", "Бункер", "Дурак онлайн", "Карты против всех", "Крокодил", "Кто я", "Монополия", "Пазлы", "Покер", "Своя игра", "Сломанный телефон", "Угадай мелодию", "Филворды", "Эволюция"]
}

# ==========================================
# --- СИСТЕМА ЛОГОВ ---
# ==========================================
async def send_log(guild, title, description, color=discord.Color.blue()):
    channel = guild.get_channel(LOG_CHANNEL_ID)
    if channel:
        embed = discord.Embed(title=title, description=description, color=color, timestamp=datetime.now())
        await channel.send(embed=embed)

# ==========================================
# --- ПАНЕЛЬ УПРАВЛЕНИЯ ИВЕНТОМ ---
# ==========================================
class EventControlView(View):
    def __init__(self, vc, tc, creator):
        super().__init__(timeout=None)
        self.vc = vc
        self.tc = tc
        self.creator = creator

    @discord.ui.button(label="Залочить/Анлок", style=discord.ButtonStyle.secondary, emoji="🔒")
    async def toggle_lock(self, interaction: discord.Interaction, button: Button):
        current = self.vc.overwrites_for(interaction.guild.default_role).connect
        state = not (current if current is not None else True)
        await self.vc.set_permissions(interaction.guild.default_role, connect=state)
        await interaction.response.send_message(f"Доступ к войсу: {'ОТКРЫТ' if state else 'ЗАКРЫТ'}", ephemeral=True)

    @discord.ui.button(label="Лимит +1", style=discord.ButtonStyle.primary, emoji="➕")
    async def add_limit(self, interaction: discord.Interaction, button: Button):
        new_limit = self.vc.user_limit + 1 if self.vc.user_limit < 99 else 99
        await self.vc.edit(user_limit=new_limit)
        await interaction.response.send_message(f"Лимит: {new_limit}", ephemeral=True)

    @discord.ui.button(label="Лимит -1", style=discord.ButtonStyle.primary, emoji="➖")
    async def sub_limit(self, interaction: discord.Interaction, button: Button):
        new_limit = self.vc.user_limit - 1 if self.vc.user_limit > 0 else 0
        await self.vc.edit(user_limit=new_limit)
        await interaction.response.send_message(f"Лимит: {new_limit}", ephemeral=True)

    @discord.ui.button(label="ЗАВЕРШИТЬ ИВЕНТ", style=discord.ButtonStyle.danger, emoji="🛑", row=1)
    async def end_event(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("Ивент завершен. Удаляю каналы...", ephemeral=True)
        await self.vc.delete()
        await self.tc.delete()
        await interaction.channel.delete()

# ==========================================
# --- СИСТЕМА ВЕРИФИКАЦИИ ---
# ==========================================
class VerifView(View):
    def __init__(self, target: discord.Member):
        super().__init__(timeout=None)
        self.target = target

    @discord.ui.button(label="Мальчик", style=discord.ButtonStyle.blurple, emoji="♂️")
    async def boy(self, interaction: discord.Interaction, button: Button):
        role = interaction.guild.get_role(ROLE_BOY)
        await self.target.add_roles(role)
        await interaction.response.edit_message(content=f"✅ {self.target.mention} верифицирован как ♂️", view=None, embed=None)
        await send_log(interaction.guild, "Верификация", f"Саппорт {interaction.user.mention} верифицировал {self.target.mention} как Мальчик", discord.Color.blue())

    @discord.ui.button(label="Девочка", style=discord.ButtonStyle.red, emoji="♀️")
    async def girl(self, interaction: discord.Interaction, button: Button):
        role = interaction.guild.get_role(ROLE_GIRL)
        await self.target.add_roles(role)
        await interaction.response.edit_message(content=f"✅ {self.target.mention} верифицирована как ♀️", view=None, embed=None)
        await send_log(interaction.guild, "Верификация", f"Саппорт {interaction.user.mention} верифицировал {self.target.mention} как Девочка", discord.Color.magenta())

# ==========================================
# --- СИСТЕМА АНКЕТ (RECRUITMENT) ---
# ==========================================
class AppModal(Modal):
    def __init__(self, post_name):
        super().__init__(title=f"Заявка: {post_name}")
        self.post_name = post_name
        self.name = TextInput(label="Имя и возраст", placeholder="Алексей, 19", min_length=2)
        self.bio = TextInput(label="О себе", style=discord.TextStyle.paragraph, placeholder="Расскажи немного о себе...")
        self.exp = TextInput(label="Опыт", style=discord.TextStyle.paragraph, placeholder="Был ли ты где-то стаффом?")
        for item in [self.name, self.bio, self.exp]: self.add_item(item)

    async def on_submit(self, interaction: discord.Interaction):
        config = STAFF_CONFIG.get(self.post_name)
        log_chan = interaction.guild.get_channel(config["log"])
        
        embed = discord.Embed(title=f"New App: {self.post_name}", color=discord.Color.gold(), timestamp=datetime.now())
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.display_avatar.url)
        embed.add_field(name="Кандидат", value=interaction.user.mention)
        embed.add_field(name="Имя/Возраст", value=self.name.value)
        embed.add_field(name="О себе", value=self.bio.value, inline=False)
        embed.add_field(name="Опыт", value=self.exp.value, inline=False)
        
        await log_chan.send(embed=embed)
        await interaction.response.send_message("✨ Твоя заявка улетела кураторам! Ожидай ответа.", ephemeral=True)

class RecruitmentView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.select(placeholder="Найти направление...", options=[discord.SelectOption(label=k) for k in STAFF_CONFIG.keys()])
    async def select_pos(self, interaction, select):
        await interaction.response.send_modal(AppModal(select.values[0]))

# ==========================================
# --- ОСНОВНОЙ БОТ ---
# ==========================================
class SuperBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=discord.Intents.all())

    async def setup_hook(self):
        g = discord.Object(id=GUILD_ID)
        self.tree.copy_global_to(guild=g)
        await self.tree.sync(guild=g)
        self.add_view(RecruitmentView())

    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.guild_id != GUILD_ID:
            return await interaction.response.send_message("Бот защищен.", ephemeral=True)
        await super().on_interaction(interaction)

bot = SuperBot()

# --- КОМАНДЫ ---

@bot.tree.command(name="create_event", description="Запустить ивент")
async def create_event(interaction: discord.Interaction):
    # Сложная логика выбора: Категория -> Игра
    view = View()
    select = Select(placeholder="Выберите категорию...")
    for cat in GAMES_DATA.keys(): select.add_item(discord.SelectOption(label=cat))
    
    async def cat_callback(inter):
        chosen_cat = select.values[0]
        game_view = View()
        game_select = Select(placeholder=f"Игры {chosen_cat}...")
        # Discord лимит 25, берем первые 25 если список больше
        for g in GAMES_DATA[chosen_cat][:25]: game_select.add_item(discord.SelectOption(label=g))
        
        async def game_callback(i):
            game = game_select.values[0]
            cat_obj = i.guild.get_channel(CAT_EVENTS_ID)
            # Создание
            vc = await cat_obj.create_voice_channel(name=f"🔊 {game}")
            tc = await cat_obj.create_text_channel(name=f"💬 {game}")
            # Управление (только ивентеру)
            overwrites = {i.guild.default_role: discord.PermissionOverwrite(view_channel=False), i.user: discord.PermissionOverwrite(view_channel=True)}
            mc = await cat_obj.create_text_channel(name=f"⚙️ упр-{game}", overwrites=overwrites)
            
            control_embed = discord.Embed(title=f"Панель ивента: {game}", description=f"Ивентер: {i.user.mention}\nТут ты можешь управлять каналами.", color=discord.Color.green())
            await mc.send(embed=control_embed, view=EventControlView(vc, tc, i.user))
            await i.response.edit_message(content=f"✅ Ивент **{game}** создан!", view=None)
            await send_log(i.guild, "Event Created", f"Ивентер {i.user.mention} создал ивент {game}", discord.Color.green())

        game_select.callback = game_callback
        game_view.add_item(game_select)
        await inter.response.edit_message(content="Теперь выберите саму игру:", view=game_view)

    select.callback = cat_callback
    view.add_item(select)
    await interaction.response.send_message("Выбор категории ивента:", view=view, ephemeral=True)

@bot.tree.command(name="hire", description="Принять на работу")
@app_commands.choices(pos=[app_commands.Choice(name=k, value=k) for k in STAFF_CONFIG.keys()])
async def hire(interaction: discord.Interaction, member: discord.Member, pos: app_commands.Choice[str]):
    # Проверка прав (Владелец, Админ или соответствующий куратор)
    conf = STAFF_CONFIG[pos.value]
    is_owner = interaction.user.id == OWNER_ID
    is_admin = any(r.id == ROLE_ADMIN_ID for r in interaction.user.roles)
    is_curator = any(r.id == conf["curator"] for r in interaction.user.roles)

    if not (is_owner or is_admin or is_curator):
        return await interaction.response.send_message("⛔ Недостаточно прав для этой ветки!", ephemeral=True)

    role = interaction.guild.get_role(conf["role"])
    await member.add_roles(role)
    await interaction.response.send_message(f"🎊 {member.mention} официально назначен на должность **{pos.value}**!")
    await send_log(interaction.guild, "Staff Update", f"{interaction.user.mention} нанял {member.mention} на роль {pos.value}", discord.Color.green())

@bot.tree.command(name="sapport_verif", description="Верификация через саппорта")
async def verif(interaction: discord.Interaction, member: discord.Member):
    # Проверка на роль саппорта (или выше)
    if not (any(r.id == STAFF_CONFIG["Саппорт"]["role"] for r in interaction.user.roles) or interaction.user.id == OWNER_ID):
        return await interaction.response.send_message("❌ Команда доступна только саппортам.", ephemeral=True)
    
    emb = discord.Embed(title="Верификация пользователя", description=f"Укажите пол для {member.mention}, чтобы выдать доступ.", color=discord.Color.orange())
    await interaction.response.send_message(embed=emb, view=VerifView(member), ephemeral=True)

@bot.command()
@commands.is_owner()
async def post_recruitment(ctx):
    emb = discord.Embed(
        title="Набор в команду XIVIVIDE",
        description="Ты проводишь время на нашем сервере и хочешь стать частью нашей команды?\n\nВыбери направление ниже, чтобы подать заявку!",
        color=discord.Color.from_rgb(47, 49, 54)
    )
    emb.set_footer(text="Мы ждем именно тебя!")
    await ctx.send(embed=emb, view=RecruitmentView())

bot.run(TOKEN)
.
