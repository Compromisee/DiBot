import discord
from discord import ui
from typing import List

# ─────────────────────────────────────────
#  Advanced Paginator
# ─────────────────────────────────────────

class Paginator(ui.View):
    """
    A full-featured paginator with navigation buttons.
    Supports embeds or plain text pages.
    """

    def __init__(
        self,
        pages: List[discord.Embed],
        author_id: int,
        timeout: int = 120,
        show_page_count: bool = True
    ):
        super().__init__(timeout=timeout)
        self.pages          = pages
        self.current        = 0
        self.author_id      = author_id
        self.show_page_count = show_page_count
        self._update_buttons()

    # ── Auth Check ───────────────────────
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(
                "❌ This paginator isn't yours!",
                ephemeral=True
            )
            return False
        return True

    # ── Button State ─────────────────────
    def _update_buttons(self):
        self.first_page.disabled  = self.current == 0
        self.prev_page.disabled   = self.current == 0
        self.next_page.disabled   = self.current == len(self.pages) - 1
        self.last_page.disabled   = self.current == len(self.pages) - 1
        self.page_counter.label   = f"{self.current + 1} / {len(self.pages)}"

    # ── Get Current Page ─────────────────
    def get_page(self) -> discord.Embed:
        page = self.pages[self.current]
        if self.show_page_count and isinstance(page, discord.Embed):
            page.set_footer(text=f"Page {self.current + 1} of {len(self.pages)}")
        return page

    # ── Buttons ───────────────────────────

    @ui.button(label="◀◀", style=discord.ButtonStyle.secondary, custom_id="paginator_first")
    async def first_page(self, interaction: discord.Interaction, button: ui.Button):
        self.current = 0
        self._update_buttons()
        await interaction.response.edit_message(embed=self.get_page(), view=self)

    @ui.button(label="◀", style=discord.ButtonStyle.primary, custom_id="paginator_prev")
    async def prev_page(self, interaction: discord.Interaction, button: ui.Button):
        self.current = max(0, self.current - 1)
        self._update_buttons()
        await interaction.response.edit_message(embed=self.get_page(), view=self)

    @ui.button(label="1 / 1", style=discord.ButtonStyle.secondary, disabled=True, custom_id="paginator_counter")
    async def page_counter(self, interaction: discord.Interaction, button: ui.Button):
        pass

    @ui.button(label="▶", style=discord.ButtonStyle.primary, custom_id="paginator_next")
    async def next_page(self, interaction: discord.Interaction, button: ui.Button):
        self.current = min(len(self.pages) - 1, self.current + 1)
        self._update_buttons()
        await interaction.response.edit_message(embed=self.get_page(), view=self)

    @ui.button(label="▶▶", style=discord.ButtonStyle.secondary, custom_id="paginator_last")
    async def last_page(self, interaction: discord.Interaction, button: ui.Button):
        self.current = len(self.pages) - 1
        self._update_buttons()
        await interaction.response.edit_message(embed=self.get_page(), view=self)

    @ui.button(label="✖ Close", style=discord.ButtonStyle.danger, custom_id="paginator_close")
    async def close(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.message.delete()
        self.stop()

    # ── Timeout ──────────────────────────
    async def on_timeout(self):
        for child in self.children:
            child.disabled = True


# ─────────────────────────────────────────
#  Helper: Build pages from a list
# ─────────────────────────────────────────

def build_pages(
    items: list,
    title: str,
    per_page: int = 10,
    color: int = 0x5865F2,
    formatter=None
) -> List[discord.Embed]:
    """
    Split a list of items into paginated embeds.

    Args:
        items:     List of items to paginate
        title:     Embed title
        per_page:  Items per page
        color:     Embed color
        formatter: Optional function(item) -> str for formatting each item

    Returns:
        List of discord.Embed
    """
    pages = []
    chunks = [items[i:i + per_page] for i in range(0, len(items), per_page)]

    for i, chunk in enumerate(chunks):
        embed = discord.Embed(title=title, color=color)
        description = ""

        for j, item in enumerate(chunk):
            index = i * per_page + j + 1
            if formatter:
                description += f"`{index}.` {formatter(item)}\n"
            else:
                description += f"`{index}.` {item}\n"

        embed.description = description or "Nothing here!"
        embed.set_footer(text=f"Page {i + 1} of {len(chunks)}")
        pages.append(embed)

    return pages if pages else [discord.Embed(title=title, description="No items found.", color=color)]