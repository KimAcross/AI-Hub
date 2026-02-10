import { Link } from 'react-router-dom'
import { Bot, MessageSquare, FileText, ArrowRight, Settings } from 'lucide-react'
import { Header } from '@/components/layout/header'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { AssistantCard } from '@/components/assistant/assistant-card'
import { useAssistants } from '@/hooks/use-assistants'
import { useAuthStore } from '@/stores/auth-store'
import { QuotaDisplay } from '@/components/quota-display'

export function DashboardPage() {
  const { data: assistants, isLoading } = useAssistants()
  const user = useAuthStore((state) => state.user)
  const isAdmin = user?.role === 'admin'

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
            <h2 className="text-lg font-semibold">
              {isAdmin ? 'Recent Assistants' : 'Available Assistants'}
            </h2>
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
                {isAdmin
                  ? 'Create your first AI assistant to get started.'
                  : 'Your administrator hasn\'t set up any assistants yet.'}
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
