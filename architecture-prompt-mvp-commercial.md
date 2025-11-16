# ARCHITECTURE PROMPT: MVP Gestion Commerciale

Flask Adaptation — Architecture & Flows (DDD + CQRS + Events)
-------------------------------------------------------------

Cette section transpose l’architecture DDD + CQRS + Domain Events + Outbox au stack Python/Flask. Les exemples .NET ci-dessous restent des références conceptuelles; l’implémentation visée est Flask.

Vue d’ensemble (Flask):
```
┌─────────────────────────────────────────────────────────┐
│                    PRESENTATION                          │
│                 (UI web design/*.html)                  │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP/REST
┌────────────────────▼────────────────────────────────────┐
│                    WEB API (Flask)                       │
│              (Blueprints + Endpoints)                    │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│              APPLICATION LAYER (CQRS)                    │
│  Commands (Write)  |  Queries (Read)                     │
│  Services applicatifs orchestrent et valident            │
└─────────┬───────────────────────────────────────┬────────┘
          │                                       │
          │                                       │ Read-Only
┌─────────▼───────────────────────────────────────▼────────┐
│                      DOMAIN LAYER                         │
│  Aggregates + invariants | Domain Events (internes)       │
│  Handlers synchrones (dispatcher Python)                  │
└───────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────▼─────────────────────────────┐
│                 INFRASTRUCTURE LAYER                      │
│  SQLAlchemy ORM | OutboxEvents (table) | Celery Worker    │
│  RabbitMQ (UNIQUEMENT pour Integration Events)            │
└───────────────────────────────────────────────────────────┘
                              │
┌───────────────────────────────────────────────────────────┐
│                    PostgreSQL Database                    │
└───────────────────────────────────────────────────────────┘
```

Principes CQRS (Flask):
- Commands: écriture, utilisent Aggregates, lèvent Domain Events, renvoient succès/échec.
- Queries: lecture seule, DTO, requêtes optimisées, hors aggregates.

Domain Events (internes):
- Traités synchronement dans la transaction (dispatcher Python).
- Restent dans le bounded context; pas d’envoi RabbitMQ.

Integration Events (externes):
- Sauvegardés en Outbox (dans la même transaction que le write).
- Publiés de manière asynchrone par un worker Celery vers RabbitMQ.

Flows:
- Domain Event Flow:
  1) Aggregate applique la commande → lève DomainEvent
  2) Dispatcher appelle DomainEventHandlers
  3) Handlers exécutent logique métier (ex: réservation stock)
  4) Commit transaction
- Integration Event Flow (Outbox):
  1) Handler mappe DomainEvent → IntegrationEvent (si besoin)
  2) Sauvegarde en Outbox dans la transaction
  3) Worker lit Outbox et publie vers RabbitMQ
  4) Systèmes externes consomment

Mapping techno:
- MediatR (.NET) → dispatcher Python simple (registre de handlers)
- EF Core → SQLAlchemy
- Hangfire → Celery (tasks + beat)
- RabbitMQ → `pika`/`kombu`

Concurrence & intégrité:
- Verrouillage pessimiste sur lignes `StockItem` pour mouvements/réservations.
- Inventaires bloquent les mouvements sur le scope jusqu’à clôture.
- Annulation de commande libère réservations dans une transaction atomique.

Sécurité & audit:
- JWT + RBAC (Admin, Direction, Commercial, Magasinier);
- Journaux d’audit `{user, action, resource, before/after, timestamp}`.

Les sections .NET suivantes illustrent les mêmes patterns; adapter les concepts à Flask selon les mappages ci-dessus.
## DDD + CQRS + Domain Events + Outbox Pattern

---

## 🎯 CONTEXTE

Vous développez un **MVP de Gestion Commerciale** avec architecture **DDD** et **CQRS**.

**IMPORTANT** : Distinction claire entre événements internes et externes :
- **Domain Events** : Communication INTERNE entre aggregates (même système)
- **Integration Events** : Communication EXTERNE vers autres projets (e-commerce, etc.)

---

## 📐 ARCHITECTURE GLOBALE

```
┌─────────────────────────────────────────────────────────┐
│                    PRESENTATION                          │
│              (Blazor WebAssembly + Fluxor)              │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP/REST
┌────────────────────▼────────────────────────────────────┐
│                  WEB API (.NET 8)                        │
│              (Controllers + Endpoints)                   │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│              APPLICATION LAYER (CQRS)                    │
│                                                          │
│  ┌──────────────┐              ┌──────────────┐        │
│  │  COMMANDS    │              │   QUERIES     │        │
│  │ (Write Side) │              │ (Read Side)   │        │
│  └──────┬───────┘              └──────┬────────┘        │
│         │                              │                 │
│         │ MediatR                      │ MediatR         │
│         ▼                              ▼                 │
│  ┌──────────────┐              ┌──────────────┐        │
│  │Command       │              │Query         │        │
│  │Handlers      │              │Handlers      │        │
│  └──────┬───────┘              └──────┬────────┘        │
└─────────┼──────────────────────────────┼─────────────────┘
          │                              │
          │                              │ Read-Only
┌─────────▼──────────────────────────────▼─────────────────┐
│                  DOMAIN LAYER                             │
│                                                           │
│  ┌────────────┐     ┌──────────────┐    ┌────────────┐  │
│  │ Aggregates │────►│Domain Events │───►│ Handlers   │  │
│  │            │     │              │    │            │  │
│  └────────────┘     └──────────────┘    └─────┬──────┘  │
│                                                 │         │
│                                                 ▼         │
│                                         ┌───────────────┐ │
│                                         │ Business      │ │
│                                         │ Logic         │ │
│                                         └───────┬───────┘ │
└─────────────────────────────────────────────────┼─────────┘
                                                  │
┌─────────────────────────────────────────────────▼─────────┐
│              INFRASTRUCTURE LAYER                          │
│                                                            │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────┐  │
│  │ EF Core      │  │ OutboxEvents │  │ Background     │  │
│  │ DbContext    │  │ Table        │  │ Worker         │  │
│  └──────────────┘  └──────┬───────┘  └────────┬───────┘  │
│                            │                    │          │
│                            │                    │          │
│  ┌─────────────────────────▼────────────────────▼───────┐ │
│  │          PostgreSQL Database                         │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐ │
│  │   RabbitMQ (UNIQUEMENT pour Integration Events)     │ │
│  │   (Communication vers projets externes)              │ │
│  └──────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────┘
```

---

## 🔑 PRINCIPES ARCHITECTURAUX

### 1. CQRS (Command Query Responsibility Segregation)

**Commands (Write Side) :**
- Modifient l'état du système
- Retournent succès/échec (pas de données)
- Utilisent les Aggregates
- Lèvent des Domain Events

**Queries (Read Side) :**
- Lecture seule
- Retournent des DTOs
- Optimisées pour la lecture
- Accès direct DB (pas d'Aggregates)

**Librairie : MediatR**

### 2. Domain-Driven Design (DDD)

**Aggregates :**
- Cluster d'entités traitées comme une unité
- Aggregate Root = point d'entrée unique
- Validation des invariants métier
- Lèvent Domain Events lors des changements d'état

**Domain Events :**
- Événements métier levés par les Aggregates
- Communication INTERNE uniquement (même système)
- Traités de manière synchrone par des handlers

**Value Objects :**
- Objets immuables sans identité
- Définis par leurs attributs
- Exemple : Money, Address, DateRange

---

## ⚡ DOMAIN EVENTS vs INTEGRATION EVENTS

### Domain Events (Internes)

**Objectif :** Communication entre Aggregates dans le même système

**Caractéristiques :**
- ✅ Traités **SYNCHRONEMENT** dans la même transaction
- ✅ Handlers appelés via **MediatR**
- ✅ **PAS d'envoi vers RabbitMQ**
- ✅ Restent dans les limites du bounded context

**Exemples :**
```
InvoiceValidatedDomainEvent
StockReservedDomainEvent
OrderPlacedDomainEvent
PaymentReceivedDomainEvent
```

**Flow :**
```
1. Aggregate.DoSomething()
   ↓
2. Raise DomainEvent
   ↓
3. MediatR dispatch → DomainEventHandlers
   ↓
4. Handler exécute logique métier
   ↓
5. Tout dans la MÊME TRANSACTION
```

---

### Integration Events (Externes)

**Objectif :** Communication vers systèmes EXTERNES (e-commerce, autres projets)

**Caractéristiques :**
- ✅ Sauvegardés dans table **OutboxEvents**
- ✅ Envoyés vers **RabbitMQ** par Background Worker
- ✅ Traitement **ASYNCHRONE**
- ✅ Communication **INTER-BOUNDED CONTEXTS**

**Exemples :**
```
InvoiceValidatedIntegrationEvent
OrderPlacedIntegrationEvent
StockLevelChangedIntegrationEvent
```

**Flow :**
```
1. DomainEvent levé
   ↓
2. DomainEventHandler exécute logique
   ↓
3. Handler mappe DomainEvent → IntegrationEvent
   ↓
4. IntegrationEvent sauvegardé dans OutboxEvents
   ↓
5. Background Worker récupère outbox non traités
   ↓
6. Publish vers RabbitMQ
   ↓
7. Projets externes (e-commerce) consomment
```

---

## 🏗️ PATTERN: Base DomainEventHandler

### Architecture du Handler

```csharp
namespace CommercialManagement.Application.Common.Handlers;

/// <summary>
/// Handler de base pour tous les Domain Events
/// Gère automatiquement la sauvegarde dans Outbox si nécessaire
/// </summary>
public abstract class DomainEventHandler<TNotification> 
    : INotificationHandler<TNotification>
    where TNotification : IDomainEvent
{
    private readonly IOutboxService _outboxService;
    private readonly ITenantContextAccessor _tenantContextAccessor;

    protected DomainEventHandler(
        IOutboxService outboxService,
        ITenantContextAccessor tenantContextAccessor)
    {
        _outboxService = outboxService;
        _tenantContextAccessor = tenantContextAccessor;
    }

    /// <summary>
    /// Méthode à implémenter pour mapper DomainEvent → IntegrationEvent
    /// Retourner null si aucun IntegrationEvent nécessaire
    /// </summary>
    protected abstract IIntegrationEvent? MapToIntegrationEvent(
        TNotification domainEvent);

    /// <summary>
    /// Point d'entrée MediatR
    /// 1. Mappe vers IntegrationEvent si nécessaire
    /// 2. Sauvegarde dans Outbox
    /// 3. Exécute logique métier
    /// </summary>
    async Task INotificationHandler<TNotification>.Handle(
        TNotification notification,
        CancellationToken cancellationToken)
    {
        // 1. Mapper vers IntegrationEvent si nécessaire
        var integrationEvent = MapToIntegrationEvent(notification);
        
        // 2. Sauvegarder dans Outbox si IntegrationEvent existe
        if (integrationEvent != null)
        {
            integrationEvent.TenantId = _tenantContextAccessor.TenantId;
            await _outboxService.AddAsync(integrationEvent, cancellationToken);
        }

        // 3. Exécuter la logique métier spécifique
        await Handle(notification);
    }

    /// <summary>
    /// Logique métier spécifique au handler
    /// </summary>
    protected abstract Task Handle(TNotification notification);
}
```

### Exemple d'utilisation

```csharp
// Domain Event
public sealed record InvoiceValidatedDomainEvent(
    int InvoiceId,
    int CustomerId,
    decimal TotalAmount,
    List<InvoiceLine> Lines
) : IDomainEvent;

// Integration Event (pour projets externes)
public sealed record InvoiceValidatedIntegrationEvent(
    int InvoiceId,
    int CustomerId,
    decimal TotalAmount,
    DateTime ValidatedAt
) : IIntegrationEvent
{
    public Guid TenantId { get; set; }
};

// Handler
public sealed class InvoiceValidatedDomainEventHandler 
    : DomainEventHandler<InvoiceValidatedDomainEvent>
{
    private readonly IStockService _stockService;
    private readonly INotificationService _notificationService;

    public InvoiceValidatedDomainEventHandler(
        IOutboxService outboxService,
        ITenantContextAccessor tenantContextAccessor,
        IStockService stockService,
        INotificationService notificationService)
        : base(outboxService, tenantContextAccessor)
    {
        _stockService = stockService;
        _notificationService = notificationService;
    }

    // Mapper DomainEvent → IntegrationEvent (pour e-commerce)
    protected override IIntegrationEvent? MapToIntegrationEvent(
        InvoiceValidatedDomainEvent domainEvent)
    {
        return new InvoiceValidatedIntegrationEvent(
            InvoiceId: domainEvent.InvoiceId,
            CustomerId: domainEvent.CustomerId,
            TotalAmount: domainEvent.TotalAmount,
            ValidatedAt: DateTime.UtcNow
        );
    }

    // Logique métier INTERNE
    protected override async Task Handle(
        InvoiceValidatedDomainEvent notification)
    {
        // 1. Réserver le stock
        await _stockService.ReserveStockForInvoice(
            notification.InvoiceId, 
            notification.Lines);

        // 2. Envoyer notification au client
        await _notificationService.NotifyInvoiceValidated(
            notification.CustomerId,
            notification.InvoiceId);

        // 3. Autres actions métier...
    }
}
```

---

## 📦 STRUCTURE PROJET

```
CommercialManagement.sln
│
├── src/
│   │
│   ├── 1. Core/
│   │   │
│   │   ├── CommercialManagement.Domain/
│   │   │   ├── Aggregates/
│   │   │   │   ├── InvoiceAggregate/
│   │   │   │   │   ├── Invoice.cs (Aggregate Root)
│   │   │   │   │   ├── InvoiceLine.cs (Entity)
│   │   │   │   │   └── InvoiceStatus.cs (Enum)
│   │   │   │   ├── OrderAggregate/
│   │   │   │   ├── ProductAggregate/
│   │   │   │   └── CustomerAggregate/
│   │   │   │
│   │   │   ├── Events/
│   │   │   │   ├── IDomainEvent.cs (interface)
│   │   │   │   ├── InvoiceValidatedDomainEvent.cs
│   │   │   │   ├── OrderPlacedDomainEvent.cs
│   │   │   │   └── StockReservedDomainEvent.cs
│   │   │   │
│   │   │   ├── ValueObjects/
│   │   │   │   ├── Money.cs
│   │   │   │   ├── Address.cs
│   │   │   │   └── DateRange.cs
│   │   │   │
│   │   │   ├── Exceptions/
│   │   │   │   ├── DomainException.cs
│   │   │   │   ├── InsufficientStockException.cs
│   │   │   │   └── InvalidInvoiceStateException.cs
│   │   │   │
│   │   │   └── Primitives/
│   │   │       ├── AggregateRoot.cs
│   │   │       ├── Entity.cs
│   │   │       └── ValueObject.cs
│   │   │
│   │   └── CommercialManagement.Application/
│   │       │
│   │       ├── Common/
│   │       │   ├── Abstractions/
│   │       │   │   ├── ICommand.cs
│   │       │   │   ├── IQuery.cs
│   │       │   │   ├── ICommandHandler.cs
│   │       │   │   ├── IQueryHandler.cs
│   │       │   │   ├── IOutboxService.cs
│   │       │   │   └── IIntegrationEvent.cs
│   │       │   │
│   │       │   ├── Handlers/
│   │       │   │   └── DomainEventHandler.cs (BASE)
│   │       │   │
│   │       │   ├── Behaviors/
│   │       │   │   ├── ValidationBehavior.cs
│   │       │   │   ├── LoggingBehavior.cs
│   │       │   │   └── TransactionBehavior.cs
│   │       │   │
│   │       │   └── Models/
│   │       │       ├── Result.cs
│   │       │       └── PaginatedList.cs
│   │       │
│   │       ├── Invoices/
│   │       │   ├── Commands/
│   │       │   │   ├── ValidateInvoice/
│   │       │   │   │   ├── ValidateInvoiceCommand.cs
│   │       │   │   │   ├── ValidateInvoiceCommandHandler.cs
│   │       │   │   │   └── ValidateInvoiceCommandValidator.cs
│   │       │   │   └── CreateInvoice/
│   │       │   │
│   │       │   ├── Queries/
│   │       │   │   ├── GetInvoices/
│   │       │   │   │   ├── GetInvoicesQuery.cs
│   │       │   │   │   └── GetInvoicesQueryHandler.cs
│   │       │   │   └── GetInvoiceById/
│   │       │   │
│   │       │   ├── Events/
│   │       │   │   ├── InvoiceValidatedDomainEventHandler.cs
│   │       │   │   └── InvoiceValidatedIntegrationEvent.cs
│   │       │   │
│   │       │   └── DTOs/
│   │       │       ├── InvoiceDto.cs
│   │       │       └── InvoiceLineDto.cs
│   │       │
│   │       ├── Orders/ (même structure)
│   │       ├── Products/ (même structure)
│   │       └── Stock/ (même structure)
│   │
│   ├── 2. Infrastructure/
│   │   │
│   │   └── CommercialManagement.Infrastructure/
│   │       │
│   │       ├── Persistence/
│   │       │   ├── ApplicationDbContext.cs
│   │       │   │
│   │       │   ├── Configurations/
│   │       │   │   ├── InvoiceConfiguration.cs
│   │       │   │   ├── OrderConfiguration.cs
│   │       │   │   └── OutboxEventConfiguration.cs
│   │       │   │
│   │       │   ├── Interceptors/
│   │       │   │   ├── DomainEventDispatcherInterceptor.cs
│   │       │   │   └── AuditableEntityInterceptor.cs
│   │       │   │
│   │       │   └── Repositories/
│   │       │       └── GenericRepository.cs
│   │       │
│   │       ├── Outbox/
│   │       │   ├── OutboxEvent.cs (Entity)
│   │       │   ├── OutboxService.cs
│   │       │   └── OutboxBackgroundWorker.cs (Hangfire)
│   │       │
│   │       ├── Messaging/
│   │       │   ├── RabbitMQ/
│   │       │   │   ├── RabbitMqPublisher.cs
│   │       │   │   └── RabbitMqConfiguration.cs
│   │       │   │
│   │       │   └── IntegrationEventPublisher.cs
│   │       │
│   │       └── DependencyInjection.cs
│   │
│   └── 3. Presentation/
│       │
│       ├── CommercialManagement.WebAPI/
│       │   ├── Controllers/
│       │   ├── Program.cs
│       │   └── appsettings.json
│       │
│       └── CommercialManagement.BlazorUI/
│           ├── Pages/
│           ├── Store/ (Fluxor State Management)
│           │   ├── Invoices/
│           │   │   ├── InvoicesState.cs
│           │   │   ├── InvoicesActions.cs
│           │   │   ├── InvoicesReducers.cs
│           │   │   └── InvoicesEffects.cs
│           │   ├── Orders/
│           │   └── Products/
│           │
│           ├── Components/
│           └── Services/
│               └── ApiClient.cs
```

---

## 🎭 FLUXOR (State Management Blazor)

### Architecture Fluxor

**Fluxor** = Redux pour Blazor

**Concepts :**
- **State** : État immutable de l'application
- **Actions** : Événements déclenchés par l'UI
- **Reducers** : Fonctions pures qui modifient le State
- **Effects** : Side effects (appels API)

**Flow :**
```
UI Component
    ↓ Dispatch
  Action
    ↓
  Reducer → New State → UI Update
    ↓
  Effect (API Call)
    ↓
  Success/Failure Action
    ↓
  Reducer → Final State → UI Update
```

### Exemple Invoices State

```csharp
// State
public record InvoicesState
{
    public bool IsLoading { get; init; }
    public List<InvoiceDto> Invoices { get; init; } = new();
    public InvoiceDto? SelectedInvoice { get; init; }
    public string? ErrorMessage { get; init; }
}

// Actions
public record LoadInvoicesAction;
public record LoadInvoicesSuccessAction(List<InvoiceDto> Invoices);
public record LoadInvoicesFailureAction(string ErrorMessage);

public record ValidateInvoiceAction(int InvoiceId);
public record ValidateInvoiceSuccessAction(int InvoiceId);
public record ValidateInvoiceFailureAction(string ErrorMessage);

// Reducers
public static class InvoicesReducers
{
    [ReducerMethod]
    public static InvoicesState OnLoadInvoices(
        InvoicesState state, 
        LoadInvoicesAction action)
    {
        return state with { IsLoading = true };
    }

    [ReducerMethod]
    public static InvoicesState OnLoadInvoicesSuccess(
        InvoicesState state,
        LoadInvoicesSuccessAction action)
    {
        return state with 
        { 
            IsLoading = false, 
            Invoices = action.Invoices,
            ErrorMessage = null
        };
    }

    [ReducerMethod]
    public static InvoicesState OnValidateInvoiceSuccess(
        InvoicesState state,
        ValidateInvoiceSuccessAction action)
    {
        var updatedInvoices = state.Invoices
            .Select(i => i.Id == action.InvoiceId 
                ? i with { Status = "Validated" } 
                : i)
            .ToList();

        return state with { Invoices = updatedInvoices };
    }
}

// Effects
public class InvoicesEffects
{
    private readonly IApiClient _apiClient;

    public InvoicesEffects(IApiClient apiClient)
    {
        _apiClient = apiClient;
    }

    [EffectMethod]
    public async Task HandleLoadInvoices(
        LoadInvoicesAction action,
        IDispatcher dispatcher)
    {
        try
        {
            var invoices = await _apiClient.GetInvoicesAsync();
            dispatcher.Dispatch(new LoadInvoicesSuccessAction(invoices));
        }
        catch (Exception ex)
        {
            dispatcher.Dispatch(
                new LoadInvoicesFailureAction(ex.Message));
        }
    }

    [EffectMethod]
    public async Task HandleValidateInvoice(
        ValidateInvoiceAction action,
        IDispatcher dispatcher)
    {
        try
        {
            await _apiClient.ValidateInvoiceAsync(action.InvoiceId);
            dispatcher.Dispatch(
                new ValidateInvoiceSuccessAction(action.InvoiceId));
        }
        catch (Exception ex)
        {
            dispatcher.Dispatch(
                new ValidateInvoiceFailureAction(ex.Message));
        }
    }
}
```

---

## ✅ CHECKLIST IMPLÉMENTATION

### ☑ Domain Layer
```
- [ ] Créer Aggregate Roots (Invoice, Order, Product, Customer, Stock)
- [ ] Implémenter méthodes métier dans Aggregates
- [ ] Lever Domain Events lors des changements d'état
- [ ] Créer Value Objects (Money, Address, DateRange)
- [ ] Définir Domain Exceptions
- [ ] Valider invariants métier
```

### ☑ Application Layer (CQRS)
```
- [ ] Installer MediatR
- [ ] Créer Commands (CreateInvoice, ValidateInvoice, etc.)
- [ ] Créer Command Handlers
- [ ] Créer Command Validators (FluentValidation)
- [ ] Créer Queries (GetInvoices, GetInvoiceById, etc.)
- [ ] Créer Query Handlers
- [ ] Créer DTOs pour réponses
- [ ] Implémenter Pipeline Behaviors (Validation, Logging, Transaction)
```

### ☑ Domain Event Handlers
```
- [ ] Créer DomainEventHandler<T> base class
- [ ] Implémenter handlers spécifiques (InvoiceValidatedDomainEventHandler)
- [ ] Mapper DomainEvents → IntegrationEvents (si externe)
- [ ] Implémenter logique métier dans Handle()
- [ ] Tester handlers unitairement
```

### ☑ Infrastructure Layer
```
- [ ] Configurer EF Core DbContext
- [ ] Créer Entity Configurations (Fluent API)
- [ ] Créer table OutboxEvents
- [ ] Implémenter OutboxService
- [ ] Créer DomainEventDispatcherInterceptor
- [ ] Configurer Transaction Management
```

### ☑ Outbox Pattern
```
- [ ] Créer OutboxEvent entity
- [ ] Implémenter IOutboxService
- [ ] Créer Background Worker (Hangfire/Quartz)
- [ ] Job récurrent : récupérer outbox non traités
- [ ] Publier vers RabbitMQ
- [ ] Marquer comme traité (IsProcessed = true)
- [ ] Gérer retry et erreurs
```

### ☑ RabbitMQ (Intégrations Externes)
```
- [ ] Installer RabbitMQ.Client ou MassTransit
- [ ] Configurer Exchange + Queues
- [ ] Implémenter Publisher
- [ ] Définir routing keys par event type
- [ ] Configurer Dead Letter Queue
- [ ] Tester publication
```

### ☑ API Layer
```
- [ ] Créer Controllers ou Minimal APIs
- [ ] Injecter IMediator
- [ ] Dispatcher Commands/Queries
- [ ] Gérer erreurs (Result pattern)
- [ ] Configurer Swagger/OpenAPI
- [ ] Ajouter validation requests
```

### ☑ Blazor UI + Fluxor
```
- [ ] Installer Fluxor.Blazor.Web
- [ ] Créer States par module
- [ ] Créer Actions
- [ ] Implémenter Reducers
- [ ] Implémenter Effects (appels API)
- [ ] Configurer Store
- [ ] Connecter Components au State
- [ ] Dispatcher Actions depuis UI
```

---

## 🔄 EXEMPLE FLOW COMPLET

### Scénario : Validation d'une Facture

**1. UI (Blazor Component)**
```csharp
// User clicks "Valider" button
@code {
    [Inject] IDispatcher Dispatcher { get; set; }

    private void OnValidateClick(int invoiceId)
    {
        Dispatcher.Dispatch(new ValidateInvoiceAction(invoiceId));
    }
}
```

**2. Fluxor Effect**
```csharp
[EffectMethod]
public async Task HandleValidateInvoice(
    ValidateInvoiceAction action,
    IDispatcher dispatcher)
{
    try
    {
        // API Call
        await _apiClient.ValidateInvoiceAsync(action.InvoiceId);
        dispatcher.Dispatch(
            new ValidateInvoiceSuccessAction(action.InvoiceId));
    }
    catch (Exception ex)
    {
        dispatcher.Dispatch(
            new ValidateInvoiceFailureAction(ex.Message));
    }
}
```

**3. API Controller**
```csharp
[HttpPost("invoices/{id}/validate")]
public async Task<IActionResult> ValidateInvoice(int id)
{
    var command = new ValidateInvoiceCommand(id);
    var result = await _mediator.Send(command);
    return result.IsSuccess ? Ok() : BadRequest(result.Error);
}
```

**4. Command Handler**
```csharp
public class ValidateInvoiceCommandHandler 
    : ICommandHandler<ValidateInvoiceCommand>
{
    private readonly IInvoiceRepository _repository;

    public async Task<Result> Handle(
        ValidateInvoiceCommand command,
        CancellationToken ct)
    {
        // 1. Récupérer Aggregate
        var invoice = await _repository.GetByIdAsync(command.InvoiceId);
        
        if (invoice == null)
            return Result.Failure("Invoice not found");

        // 2. Exécuter logique métier sur Aggregate
        invoice.Validate(); // ← Lève InvoiceValidatedDomainEvent

        // 3. Sauvegarder (UnitOfWork)
        await _repository.UpdateAsync(invoice);
        await _repository.UnitOfWork.SaveChangesAsync(ct);

        return Result.Success();
    }
}
```

**5. Aggregate (Domain)**
```csharp
public class Invoice : AggregateRoot
{
    public InvoiceStatus Status { get; private set; }
    public List<InvoiceLine> Lines { get; private set; }
    
    public void Validate()
    {
        // Validation métier
        if (Status != InvoiceStatus.Draft)
            throw new InvalidInvoiceStateException(
                "Only draft invoices can be validated");

        if (!Lines.Any())
            throw new DomainException(
                "Invoice must have at least one line");

        // Changement d'état
        Status = InvoiceStatus.Validated;

        // ⚡ LEVER DOMAIN EVENT
        RaiseDomainEvent(new InvoiceValidatedDomainEvent(
            InvoiceId: Id,
            CustomerId: CustomerId,
            TotalAmount: GetTotalAmount(),
            Lines: Lines
        ));
    }
}
```

**6. DbContext Interceptor**
```csharp
public override async Task<int> SaveChangesAsync(
    CancellationToken ct = default)
{
    // 1. Récupérer Domain Events des Aggregates
    var domainEvents = ChangeTracker
        .Entries<AggregateRoot>()
        .SelectMany(e => e.Entity.DomainEvents)
        .ToList();

    // 2. Sauvegarder changements DB
    var result = await base.SaveChangesAsync(ct);

    // 3. Dispatcher Domain Events (MediatR)
    foreach (var domainEvent in domainEvents)
    {
        await _mediator.Publish(domainEvent, ct);
    }

    return result;
}
```

**7. Domain Event Handler**
```csharp
public class InvoiceValidatedDomainEventHandler 
    : DomainEventHandler<InvoiceValidatedDomainEvent>
{
    private readonly IStockService _stockService;

    protected override IIntegrationEvent? MapToIntegrationEvent(
        InvoiceValidatedDomainEvent domainEvent)
    {
        // Mapper vers Integration Event (pour e-commerce)
        return new InvoiceValidatedIntegrationEvent(
            InvoiceId: domainEvent.InvoiceId,
            CustomerId: domainEvent.CustomerId,
            TotalAmount: domainEvent.TotalAmount,
            ValidatedAt: DateTime.UtcNow
        );
        // ↑ Cet event sera sauvegardé dans OutboxEvents
    }

    protected override async Task Handle(
        InvoiceValidatedDomainEvent notification)
    {
        // 🔥 LOGIQUE MÉTIER INTERNE

        // 1. Réserver le stock
        await _stockService.ReserveStockForInvoice(
            notification.InvoiceId,
            notification.Lines);

        // 2. Autres actions...
    }
}
```

**8. Outbox Service (sauvegarde automatique)**
```csharp
// Dans DomainEventHandler base :
if (integrationEvent != null)
{
    integrationEvent.TenantId = _tenantContextAccessor.TenantId;
    await _outboxService.AddAsync(integrationEvent, ct);
}

// OutboxService.AddAsync :
public async Task AddAsync(
    IIntegrationEvent integrationEvent,
    CancellationToken ct)
{
    var outboxEvent = new OutboxEvent
    {
        Id = Guid.NewGuid(),
        EventType = integrationEvent.GetType().FullName,
        EventData = JsonSerializer.Serialize(integrationEvent),
        OccurredOn = DateTime.UtcNow,
        IsProcessed = false
    };

    _dbContext.OutboxEvents.Add(outboxEvent);
    await _dbContext.SaveChangesAsync(ct);
}
```

**9. Background Worker (Hangfire)**
```csharp
[AutomaticRetry(Attempts = 3)]
public async Task ProcessOutboxEventsAsync()
{
    // 1. Récupérer événements non traités
    var events = await _dbContext.OutboxEvents
        .Where(e => !e.IsProcessed)
        .OrderBy(e => e.OccurredOn)
        .Take(100)
        .ToListAsync();

    foreach (var outboxEvent in events)
    {
        try
        {
            // 2. Publier vers RabbitMQ
            await _rabbitMqPublisher.PublishAsync(
                outboxEvent.EventType,
                outboxEvent.EventData);

            // 3. Marquer comme traité
            outboxEvent.IsProcessed = true;
            outboxEvent.ProcessedOn = DateTime.UtcNow;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, 
                "Failed to publish outbox event {EventId}", 
                outboxEvent.Id);
            // Retry automatique via Hangfire
        }
    }

    await _dbContext.SaveChangesAsync();
}
```

**10. RabbitMQ Publisher**
```csharp
public async Task PublishAsync(string eventType, string eventData)
{
    var routingKey = eventType.Replace("IntegrationEvent", "")
                              .ToLowerInvariant();
    
    // Ex: invoices.validated
    
    var properties = _channel.CreateBasicProperties();
    properties.Persistent = true;
    properties.ContentType = "application/json";

    _channel.BasicPublish(
        exchange: "commercial-management",
        routingKey: routingKey,
        basicProperties: properties,
        body: Encoding.UTF8.GetBytes(eventData)
    );

    await Task.CompletedTask;
}
```

**11. Fluxor Reducer (UI Update)**
```csharp
[ReducerMethod]
public static InvoicesState OnValidateInvoiceSuccess(
    InvoicesState state,
    ValidateInvoiceSuccessAction action)
{
    var updatedInvoices = state.Invoices
        .Select(i => i.Id == action.InvoiceId
            ? i with { Status = "Validated" }
            : i)
        .ToList();

    return state with { Invoices = updatedInvoices };
}
```

**12. UI Component (Auto-Update)**
```csharp
@inherits FluxorComponent

<MudDataGrid Items="@InvoicesState.Value.Invoices">
    <!-- Auto-refresh when state changes -->
</MudDataGrid>

@code {
    [Inject] IState<InvoicesState> InvoicesState { get; set; }
}
```

---

## 📊 RÉSUMÉ FLOW

```
┌──────────────────────────────────────────────────────────┐
│                   DOMAIN EVENTS FLOW                      │
└──────────────────────────────────────────────────────────┘

1. UI Button Click
   ↓
2. Dispatch Fluxor Action
   ↓
3. Fluxor Effect → API Call
   ↓
4. API Controller → MediatR Command
   ↓
5. Command Handler → Aggregate
   ↓
6. Aggregate.Validate() → Raise DomainEvent
   ↓
7. SaveChanges → Interceptor → Publish DomainEvent (MediatR)
   ↓
8. DomainEventHandler:
   ├─ MapToIntegrationEvent → Save to OutboxEvents
   └─ Handle() → Execute Business Logic (INTERNAL)
   ↓
9. Background Worker (Every 30s)
   ├─ Get Unprocessed Outbox Events
   ├─ Publish to RabbitMQ
   └─ Mark as Processed
   ↓
10. External Projects (E-commerce) Consume from RabbitMQ
   ↓
11. Fluxor Success Action → Reducer → State Update
   ↓
12. UI Auto-Refresh
```

---

## 🔑 RÈGLES IMPORTANTES

### ✅ À FAIRE

1. **Aggregates :**
   - Toujours modifier via Aggregate Root
   - Valider invariants métier
   - Lever Domain Events pour changements importants

2. **Domain Events :**
   - Nommer au passé (InvoiceValidated, NOT ValidateInvoice)
   - Rendre immutables (records)
   - Traités synchronement (MediatR)
   - Communication INTERNE uniquement

3. **Integration Events :**
   - Créer UNIQUEMENT si communication externe nécessaire
   - Toujours sauvegarder dans Outbox
   - JAMAIS publier directement à RabbitMQ depuis domain

4. **CQRS :**
   - Commands modifient via Aggregates
   - Queries lecture directe (DTOs)
   - Séparer clairement Write/Read

5. **Fluxor :**
   - State immutable (records with)
   - Reducers pure functions
   - Effects pour side effects (API)

### ❌ À ÉVITER

1. **NE PAS** modifier plusieurs Aggregates dans même transaction
2. **NE PAS** appeler directement RabbitMQ depuis Domain/Application
3. **NE PAS** publier IntegrationEvents pour communication interne
4. **NE PAS** ignorer Domain Events
5. **NE PAS** exposer entités domain à l'UI (utiliser DTOs)
6. **NE PAS** mettre logique métier dans Controllers
7. **NE PAS** muter State Fluxor directement (use Reducers)

---

## 📚 TECHNOLOGIES & LIBRAIRIES

### Backend (.NET 8)
```
✅ MediatR (CQRS + Domain Events)
✅ FluentValidation (Validation)
✅ Entity Framework Core 8 (ORM)
✅ PostgreSQL (Database)
✅ Hangfire (Background Jobs)
✅ RabbitMQ.Client ou MassTransit (Messaging)
✅ Serilog (Logging)
✅ AutoMapper ou Mapster (Mapping)
```

### Frontend (Blazor WebAssembly)
```
✅ Fluxor (State Management)
✅ MudBlazor (UI Components)
✅ Refit (API Client)
```

---

## 📝 EXEMPLE NAMING CONVENTIONS

### Domain Events
```
✅ InvoiceValidatedDomainEvent
✅ OrderPlacedDomainEvent
✅ PaymentReceivedDomainEvent
✅ StockReservedDomainEvent
```

### Integration Events
```
✅ InvoiceValidatedIntegrationEvent
✅ OrderPlacedIntegrationEvent
✅ StockLevelChangedIntegrationEvent
```

### Commands
```
✅ ValidateInvoiceCommand
✅ CreateOrderCommand
✅ UpdateProductCommand
```

### Queries
```
✅ GetInvoicesQuery
✅ GetInvoiceByIdQuery
✅ GetCustomerOrdersQuery
```

---

**END OF PROMPT**

Utilisez cette architecture pour générer un système robuste, scalable et maintenable avec séparation claire entre :
- Communication INTERNE (Domain Events)
- Communication EXTERNE (Integration Events via Outbox + RabbitMQ)
