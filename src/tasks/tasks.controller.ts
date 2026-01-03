import { Controller, Get, Post, Body, Patch, Param, Delete, Put, ConflictException } from '@nestjs/common';
import { TasksService } from './tasks.service';
import { CreateTaskDto } from './dto/create-task.dto';
import { UpdateTaskDto } from './dto/update-task.dto';

@Controller('tasks')
export class TasksController {
  constructor(private readonly tasksService: TasksService) {}

  @Post('create')
  async create(@Body() createTaskDto: CreateTaskDto) {
    const task = await this.tasksService.create(createTaskDto);
    return {
      message: 'task added',
      data: task,
    };
  }

  @Get()
  async findAll() {
    const task = await this.tasksService.findAll();
    return {
      message: 'task list',
      data: task,
    };
  }


  @Get(':id')
  async findOne(@Param('id') id: string) {
    const task = await this.tasksService.findone(+id);
    if (!task) {
      return {
        message: 'task not found',
        data: {},
      };
    }
    return {
      message: 'task found',
      data: task,
    };
  }


@Put(':id')
async update(
  @Param('id') id: string,
  @Body() UpdateTaskDto: UpdateTaskDto,
) {
  // First, check if the task exists
  const task = await this.tasksService.findone(+id);

    if (!task) {
      return {
        message: 'task not found',
        data: {},
      };
    }

    // Only check for duplicate name if the name is being updated and it's different
    if (UpdateTaskDto.title && UpdateTaskDto.title !== task.title) {
      const existingtask = await this.tasksService.findBy({
        where: { title: UpdateTaskDto.title },
      });

      if (existingtask) {
        throw new ConflictException('Task with this name already exists');
      }
    }

    const updatedtask = await this.tasksService.update(
      +id,
      UpdateTaskDto,
    );

    return {
      message: 'task updated successfully',
      data: updatedtask,
    };
  }


@Delete(':id')
  async remove(@Param('id') id: string) {
    const task = await this.tasksService.findone(+id);

    if (!task) {
      return {
        message: 'task not found',
        data: {},
      };
    }

    await this.tasksService.remove(+id);

    return {
      message: 'task deleted successfully',
      data: task,
    };
  }
}
