"""podcast/views.py"""
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import Podcast, PodcastCategory, PodcastSeries

GRADIENTS = [
    "linear-gradient(135deg,#667eea,#764ba2)",
    "linear-gradient(135deg,#f093fb,#f5576c)",
    "linear-gradient(135deg,#4facfe,#00f2fe)",
    "linear-gradient(135deg,#fa709a,#fee140)",
    "linear-gradient(135deg,#a8edea,#fed6e3)",
    "linear-gradient(135deg,#ff9a9e,#fecfef)",
    "linear-gradient(135deg,#ffecd2,#fcb69f)",
    "linear-gradient(135deg,#a1c4fd,#c2e9fb)",
    "linear-gradient(135deg,#d299c2,#fef9d7)",
    "linear-gradient(135deg,#f6d365,#fda085)",
    "linear-gradient(135deg,#84fab0,#8fd3f4)",
    "linear-gradient(135deg,#96deda,#50c9c3)",
]
ICONS = ["quran","microphone-alt","mosque","music","headphones","podcast","scroll","feather","dove","star-and-crescent","hands-praying","crown"]


def _enrich(qs):
    items = list(qs)
    for p in items:
        idx = p.pk % len(GRADIENTS)
        p.gradient  = GRADIENTS[idx]
        p.cover_icon= ICONS[idx % len(ICONS)]
    return items


def podcasts_list(request):
    categories = PodcastCategory.objects.filter(parent__isnull=True).order_by('order')
    grouped = {}
    for cat in categories:
        pods = _enrich(
            Podcast.objects.filter(is_active=True, category=cat)
            .select_related('category','series')
            .order_by('-created_at')[:8]
        )
        if pods:
            grouped[cat] = pods

    featured = Podcast.objects.filter(is_active=True, is_featured=True).first()
    if featured:
        idx = featured.pk % len(GRADIENTS)
        featured.gradient   = GRADIENTS[idx]
        featured.cover_icon = ICONS[idx % len(ICONS)]

    return render(request, 'podcasts/podcasts.html', {
        'grouped_podcasts': grouped,
        'featured':         featured,
        'active_menu':      'podcasts',
    })


def podcast_detail(request, slug):
    podcast = get_object_or_404(Podcast, slug=slug, is_active=True)
    Podcast.objects.filter(pk=podcast.pk).update(plays=podcast.plays + 1)

    idx = podcast.pk % len(GRADIENTS)
    podcast.gradient   = GRADIENTS[idx]
    podcast.cover_icon = ICONS[idx % len(ICONS)]

    # قسمت‌های همین مجموعه
    series_episodes = []
    if podcast.series:
        series_episodes = _enrich(
            Podcast.objects.filter(series=podcast.series, is_active=True)
            .exclude(pk=podcast.pk)
            .order_by('episode_number')[:12]
        )

    # بررسی دسترسی
    from purchase.models import Purchase
    has_access = (
        podcast.access_type == 'free'
        or Purchase.has_access(request.user, 'podcast', podcast.pk)
    )

    return render(request, 'podcasts/podcast_detail.html', {
        'podcast':         podcast,
        'series_episodes': series_episodes,
        'has_access':      has_access,
        'active_menu':     'podcasts',
    })


def podcasts_by_category(request, slug):
    category = get_object_or_404(PodcastCategory, slug=slug)
    qs = Podcast.objects.filter(is_active=True, category=category).select_related('series')

    q      = request.GET.get('q', '').strip()
    access = request.GET.get('access', '')
    sort   = request.GET.get('sort', '-created_at')

    if q:
        qs = (qs.filter(title__icontains=q) | qs.filter(host__icontains=q)).distinct()
    if access in ('free','paid','premium'):
        qs = qs.filter(access_type=access)
    if sort not in ('-created_at','-plays','-rating','price','-price'):
        sort = '-created_at'
    qs = qs.order_by(sort)

    paginator = Paginator(qs, 12)
    page_obj  = paginator.get_page(request.GET.get('page', 1))
    podcasts  = _enrich(page_obj.object_list)

    return render(request, 'podcasts/podcasts_category.html', {
        'category':        category,
        'page_obj':        page_obj,
        'podcasts':        podcasts,
        'search_query':    q,
        'selected_access': access,
        'selected_sort':   sort,
        'active_menu':     'podcasts',
    })