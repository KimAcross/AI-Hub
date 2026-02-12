import { Link } from 'react-router-dom'
import { Bot, MessageSquare, FileText, ArrowRight, Settings } from 'lucide-react'
import { Header } from '@/components/layout/header'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { AssistantCard } from '@/components/assistant/assistant-card'
import { useAssistants } from '@/hooks/use-assistants'
import { useAuthStore } from '@/stores/auth-store'
import { QuotaDisplay } from '@/components/quota-display'

function UserDashboard() {
  const { data: assistants, isLoading } = useAssistants()
  const user = useAuthStore((state) => state.user)
  const activeAssistants = assistants?.filter(a => !a.is_deleted) ?? []

  return (
    <div className="flex flex-col h-screen">
      <Header title="Dashboard" />

      <div className="flex-1 overflow-auto p-6">
        {/* Welcome */}
        <div className="mb-8">
          <h1 className="text-2xl font-bold">
            Hello, {user?.name?.split(' ')[0] || 'there'}
          </h1>
          <p className="text-muted-foreground mt-1">
            Choose an assistant to start chatting
          </p>
        </div>

        {/* Assistant Grid */}
        {isLoading ? (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            {[1, 2, 3, 4].map((i) => (
              <Card key={i} className="p-5">
                <div className="flex items-center gap-3 mb-3">
                  <Skeleton className="h-12 w-12 rounded-full" />
                  <div className="flex-1">
                    <Skeleton className="h-4 w-28 mb-2" />
                    <Skeleton className="h-3 w-20" />
                  </div>
                </div>
                <Skeleton className="h-4 w-full mb-1" />
                <Skeleton className="h-4 w-2/3" />
              </Card>
            ))}
          </div>
        ) : (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            {/* Start Chat card — visually distinct from assistant cards */}
            <Link to="/chat" className="block">
              <Card className="h-full bg-primary/5 border-primary/20 hover:bg-primary/10 hover:shadow-md transition-all cursor-pointer">
                <div className="flex flex-col items-center justify-center text-center p-6 h-full min-h-[160px]">
                  <div className="flex h-14 w-14 items-center justify-center rounded-full bg-primary text-primary-foreground mb-3">
                    <MessageSquare className="h-7 w-7" />
                  </div>
                  <h3 className="font-semibold text-primary">New Chat</h3>
                  <p className="text-sm text-muted-foreground mt-1">
                    Chat without an assistant
                  </p>
                </div>
              </Card>
            </Link>

            {/* Assistant cards */}
            {activeAssistants.map((assistant) => (
              <Link key={assistant.id} to={`/chat?assistant=${assistant.id}`} className="block">
                <Card className="h-full hover:shadow-md transition-all cursor-pointer">
                  <div className="p-5">
                    <div className="flex items-center gap-3 mb-3">
                      <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-primary/10">
                        {assistant.avatar_url ? (
                          <img
                            src={assistant.avatar_url}
                            alt={assistant.name}
                            className="h-12 w-12 rounded-full object-cover"
                          />
                        ) : (
                          <Bot className="h-6 w-6 text-primary" />
                        )}
                      </div>
                      <div className="min-w-0 flex-1">
                        <h3 className="font-semibold truncate">{assistant.name}</h3>
                        <Badge variant="secondary" className="text-xs mt-0.5">
                          {assistant.model.split('/').pop()}
                        </Badge>
                      </div>
                    </div>
                    {assistant.description && (
                      <p className="text-sm text-muted-foreground line-clamp-2">
                        {assistant.description}
                      </p>
                    )}
                    {(assistant.files_count ?? 0) > 0 && (
                      <div className="flex items-center gap-1 text-xs text-muted-foreground mt-2">
                        <FileText className="h-3.5 w-3.5" />
                        <span>{assistant.files_count} knowledge files</span>
                      </div>
                    )}
                  </div>
                </Card>
              </Link>
            ))}

            {activeAssistants.length === 0 && (
              <Card className="col-span-full p-8 text-center">
                <Bot className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                <h3 className="font-semibold mb-2">No assistants available yet</h3>
                <p className="text-muted-foreground">
                  Your administrator hasn't set up any assistants yet.
                </p>
              </Card>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

function AdminDashboard() {
  const { data: assistants, isLoading } = useAssistants()
  const activeAssistants = assistants?.filter(a => !a.is_deleted) ?? []
  const totalFiles = activeAssistants.reduce((sum, a) => sum + (a.files_count ?? 0), 0)

  return (
    <div className="flex flex-col h-screen">
      <Header title="Dashboard" />

      <div className="flex-1 overflow-auto p-6">
        {/* Stats */}
        <div className="grid gap-4 md:grid-cols-3 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Assistants</CardTitle>
              <Bot className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{activeAssistants.length}</div>
              <p className="text-xs text-muted-foreground">Available assistants</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Knowledge Files</CardTitle>
              <FileText className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{totalFiles}</div>
              <p className="text-xs text-muted-foreground">Uploaded documents</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Conversations</CardTitle>
              <MessageSquare className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">-</div>
              <p className="text-xs text-muted-foreground">Your conversations</p>
            </CardContent>
          </Card>
        </div>

        {/* Quota Display */}
        <div className="mb-8">
          <QuotaDisplay />
        </div>

        {/* Recent Assistants */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">Recent Assistants</h2>
            <Button variant="ghost" size="sm" asChild>
              <Link to="/assistants">
                Browse All
                <ArrowRight className="h-4 w-4 ml-1" />
              </Link>
            </Button>
          </div>

          {isLoading ? (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {[1, 2, 3].map((i) => (
                <Card key={i}>
                  <CardHeader className="pb-3">
                    <div className="flex items-center gap-3">
                      <Skeleton className="h-10 w-10 rounded-full" />
                      <div className="flex-1">
                        <Skeleton className="h-4 w-32 mb-2" />
                        <Skeleton className="h-3 w-24" />
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <Skeleton className="h-4 w-full mb-2" />
                    <Skeleton className="h-4 w-2/3" />
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : activeAssistants.length > 0 ? (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {activeAssistants.slice(0, 6).map((assistant) => (
                <AssistantCard
                  key={assistant.id}
                  assistant={assistant}
                />
              ))}
            </div>
          ) : (
            <Card className="p-8 text-center">
              <Bot className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
              <h3 className="font-semibold mb-2">No assistants available yet</h3>
              <p className="text-muted-foreground mb-4">
                Create your first AI assistant to get started.
              </p>
            </Card>
          )}
        </div>

        {/* Quick Actions */}
        <div>
          <h2 className="text-lg font-semibold mb-4">Quick Actions</h2>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            <Card className="cursor-pointer hover:shadow-md transition-shadow">
              <Link to="/assistants" className="block p-4">
                <Bot className="h-8 w-8 text-primary mb-2" />
                <h3 className="font-medium">Browse Assistants</h3>
                <p className="text-sm text-muted-foreground">View available AI assistants</p>
              </Link>
            </Card>
            <Card className="cursor-pointer hover:shadow-md transition-shadow">
              <Link to="/chat" className="block p-4">
                <MessageSquare className="h-8 w-8 text-primary mb-2" />
                <h3 className="font-medium">Start Chat</h3>
                <p className="text-sm text-muted-foreground">Begin a conversation</p>
              </Link>
            </Card>
            <Card className="cursor-pointer hover:shadow-md transition-shadow">
              <Link to="/settings" className="block p-4">
                <Settings className="h-8 w-8 text-primary mb-2" />
                <h3 className="font-medium">Settings</h3>
                <p className="text-sm text-muted-foreground">Customize your experience</p>
              </Link>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}

export function DashboardPage() {
  const user = useAuthStore((state) => state.user)
  const isAdmin = user?.role === 'admin'

  return isAdmin ? <AdminDashboard /> : <UserDashboard />
}
